import html
import logging
import os
import shlex
from subprocess import Popen, PIPE

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from genomespaceclient import GenomeSpaceClient
from openid.consumer import consumer

from agrf.local_settings import TRUST_ROOT, RETURN_TO_URL, LOGOUT_TAIL, \
    BASE_DIRECTORY, CMD_ENVIRONMENT
from agrf_feed.apps import AgrfFeedConfig
from agrf_feed.forms import FileUploadForm, TargetChooserForm, \
    GenomeSpaceLoginForm

# Useful links
# http://www.genomespace.org/support/api/openid-requirements
# http://identity.genomespace.org/openid/
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication

# The following are keys used for values stored in the session
S_LOCATION = 'xrd_location'  # The location of the GenomeSpace we are using
S_GS_TOKEN = 'gs-token'  # The GenomeSpace token
S_GS_USERNAME = 'gs-username'  # The GenomeSpace user name
S_SOURCE_FILES = 'source_files'  # The list of files we can upload
S_CHOSEN_FILES = 'files'  # The list of files we want to upload
S_TARGETS = 'targets'  # The list of target directories that we can upload to


def index(request):
    # template = loader.get_template('agrf_feed/index.html')
    return render(request, 'agrf_feed/index.html')
    # return HttpResponse(template.render(request))


def _handle_genomespace_callback(request):
    token = request.GET.get('openid.ext1.gs-token', None)
    username = request.GET.get('openid.ext1.gs-username', None)
    if not token or not username:
        token = request.COOKIES.get(S_GS_TOKEN, None)
        username = request.COOKIES.get(S_GS_USERNAME, None)
    if not token or not username:
        logging.error("login failed...")
        messages.add_message(request, messages.ERROR, "Login failed")
        return HttpResponseRedirect('/')
    request.session[S_GS_TOKEN] = token
    request.session[S_GS_USERNAME] = username
    next_form = '/target_selector' if request.session.get(S_CHOSEN_FILES,
                                                          None) else '/files'
    return HttpResponseRedirect(next_form)


def _do_gs_login(form, request):
    xrd_location = form.cleaned_data['xrd_provider']
    request.session[S_LOCATION] = xrd_location
    # Now, if we provide a store
    #    store = memstore.MemoryStore()
    # we get errors:
    # ERROR:root:Missing required parameter in response from ...
    #    ('http://openid.net/signon/1.0', 'assoc_type')
    # https://github.com/jbufu/openid4java/issues/192
    # gives a clue: perhaps the Genomespace operates in stateless mode?
    # If we construct our consumer with None for the store it will
    # operate only in stateless mode - and there are no errors
    oid_consumer = consumer.Consumer(request.session, None)
    try:
        xrd_url = AgrfFeedConfig.get_openid_server(xrd_location)
        oid_request = oid_consumer.begin(xrd_url)
        if oid_request is None:
            error_message = 'No OpenId Services found for %s' % xrd_location
            logging.error(error_message)
            messages.add_message(request, messages.ERROR, error_message)
            return HttpResponseRedirect('/')
        return redirect(oid_request.redirectURL(TRUST_ROOT, RETURN_TO_URL))
    except consumer.DiscoveryFailure as exc:
        error_message = 'Error in discovery: %s' % (html.escape(str(exc)))
        logging.error(error_message)
        messages.add_message(request, messages.ERROR, error_message)
        return HttpResponseRedirect('/')


@login_required
def gs_login(request):
    if request.method == 'POST':
        form = GenomeSpaceLoginForm(request.POST)
        if form.is_valid():
            return _do_gs_login(form, request)
    else:
        if 'true' == request.GET.get('is_return', 'false'):
            return _handle_genomespace_callback(request)
        form = GenomeSpaceLoginForm(initial={'next': '/target_selector'})
    return render(request, 'agrf_feed/gs_login.html', {'form': form})


def gs_token_required(func):
    """
    Decorator that makes sure that the user has a GenomeSpace token
    """

    def _wrapper(request, *args, **kwargs):
        if not request.session.get(S_GS_TOKEN, None):
            return HttpResponseRedirect('/gs_login')
        return func(request, *args, **kwargs)

    return _wrapper


def gs_logout(request):
    logging.info(
        'User %s logging out of the GenomeSpace' % request.user.get_username())
    # remove genomespace info
    request.session[S_GS_TOKEN] = None
    request.session[S_GS_USERNAME] = None
    request.session[S_CHOSEN_FILES] = None
    xrd_location = request.session.get(S_LOCATION, None)
    if not xrd_location:
        return HttpResponseRedirect('/')
    request.session[S_LOCATION] = None
    # do openid logout
    # we have:
    #   https://identity.genomespace.org/identityServer/xrd.jsp
    # we want:
    #   https://identity.genomespace.org/identityServer/openIdProvider?_action=logout
    xrd_url = AgrfFeedConfig.get_openid_server(xrd_location)
    xrd_url = xrd_url.replace('xrd.jsp', LOGOUT_TAIL)
    return redirect(xrd_url)


def get_users_files(user):
    """
    Path to user data = /ftp-home/$USER/files
    This application will need permissions to read those directories...
    """
    if not user.is_authenticated():
        # shouldn't always be authenticated, but...
        return tuple()
    path = "/ftp-home/%s/files" % user.username
    if not os.path.exists(path):
        path = BASE_DIRECTORY
    # should these be html escaped? Check the form library...
    return tuple((os.path.join(root, name), name)
                 for root, dirs, files in os.walk(path)
                 for name in files
                 if not name.startswith('.'))


@never_cache
@login_required
def files_selector(request):
    if request.method == 'POST' and request.session[S_SOURCE_FILES]:
        source_files = request.session[S_SOURCE_FILES]
        form = FileUploadForm(source_files, request.POST)
        if form.is_valid():
            request.session[S_CHOSEN_FILES] = form.cleaned_data['file_listing']
            request.session[S_SOURCE_FILES] = None
            return HttpResponseRedirect('/target_selector')
    else:
        source_files = get_users_files(request.user)
        request.session[S_SOURCE_FILES] = source_files
        form = FileUploadForm(source_files)
    return render(request, 'agrf_feed/files.html', {'form': form})


def _list_directories(client, folder_url, username):
    """
    Will throw an exception if the genomespace bucket provider key has expired
    or changed.
    Can return an empty list if there are no buckets for the user to write to
    """
    result = []
    folder_contents = client.list(folder_url)
    for folder in folder_contents["contents"]:
        # ignore all non directory artifacts
        if not folder["isDirectory"]:
            continue
        # ignore all the public subdirectories
        if folder['path'].startswith('/Home/Public'):
            continue
        for permission in folder["effectiveAcl"]["accessControlEntries"]:
            if "W" == permission["permission"] \
                    and "User" == permission["sid"]["type"] \
                    and permission["sid"]["name"] == username:
                # we have a target we can upload a file to
                entry = {
                    'owner': folder["owner"]["name"],
                    'name': folder.get("name"),
                    'path': folder.get("path"),
                    'url': folder.get("url")
                }
                result.append(entry)
                break  # no need to carry on looking at permissions
        # look for subdirectories
        result.extend(
            _list_directories(client, folder.get("url"), username)
        )
    return result


def _move_files_to_gs(dirs, selected_dir, request):
    target_dir = None
    for target in dirs:
        if target['path'] == selected_dir:
            target_dir = target
            break
    if target_dir:
        token = request.session[S_GS_TOKEN]
        # client = GenomeSpaceClient(token=request.session[S_GS_TOKEN])
        for escaped_path in request.session[S_CHOSEN_FILES]:
            path = html.unescape(escaped_path)
            file_name = os.path.basename(path)
            bucket = target_dir['url'] + '/' + file_name
            path = shlex.quote(path)
            bucket = shlex.quote(bucket)
            # client.copy(path, bucket))
            # above fails if not run on main thread, so...
            # also, following will fail if filename has a " in it...

            cmd = """%s genomespace -t %s cp %s %s """ % (
                CMD_ENVIRONMENT, token, path, bucket)
            (out, err) = Popen(cmd, stdin=PIPE, stdout=PIPE,
                               stderr=PIPE, close_fds=True,
                               shell=True).communicate(None)
            if err:
                message = """Error uploading %s""" % file_name
                messages.add_message(request, messages.ERROR, message)
                message = "%s as: %s" % (message, err)
                logging.error(message)
            else:
                message = """Successfully uploaded %s""" % file_name
                messages.add_message(request, messages.INFO, message)
                logging.info(message)
        # Remove our list of files to upload from the session
        request.session[S_CHOSEN_FILES] = None
    else:
        messages.add_message(request, messages.ERROR,
                             'No target directory was selected?')
    return HttpResponseRedirect('/files')


@never_cache
@login_required
@gs_token_required
def target_selector(request):
    if not request.session.get(S_CHOSEN_FILES, None):
        messages.add_message(request, messages.INFO,
                             'Please choose the files you want to upload')
        return HttpResponseRedirect('/files')
    if request.method == 'POST' and request.session[S_TARGETS]:
        target_directories = request.session[S_TARGETS]
        targets = tuple((s['path'], s['name']) for s in target_directories)
        form = TargetChooserForm(targets, request.POST)
        if form.is_valid():
            selected_dir = form.cleaned_data['target_directories']
            return _move_files_to_gs(target_directories, selected_dir, request)
    else:
        client = GenomeSpaceClient(token=request.session[S_GS_TOKEN])
        xrd_location = request.session[S_LOCATION]
        dm_server = AgrfFeedConfig.get_dm_server(xrd_location)
        home_dir = dm_server + "/v1.0/file/Home/"
        target_directories = _list_directories(
            client,
            home_dir,
            request.session[S_GS_USERNAME]
        )
        request.session[S_TARGETS] = target_directories
        targets = tuple((s['path'], s['path']) for s in target_directories)
        form = TargetChooserForm(targets)
    return render(request, 'agrf_feed/targets.html', {'form': form})

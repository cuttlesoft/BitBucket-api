# -*- coding: utf-8 -*-
from tempfile import NamedTemporaryFile
from zipfile import ZipFile


URLS = {
    'CREATE_REPO': 'repositories/%(username)s/%(repo_slug)s',
    'GET_ALL': 'repositories/%(username)s/',
    'GET_REPO': 'repositories/%(username)s/%(repo_slug)s/',
    'UPDATE_REPO': 'repositories/%(username)s/%(repo_slug)s/',
    'DELETE_REPO': 'repositories/%(username)s/%(repo_slug)s/',
    # Get archive
    'GET_ARCHIVE': 'repositories/%(username)s/%(repo_slug)s/%(format)s/master/',
}


class Repository(object):
    """ This class provide repository-related methods to Bitbucket objects."""

    def __init__(self, bitbucket):
        self.bitbucket = bitbucket
        self.bitbucket.URLS.update(URLS)

    def _get_files_in_dir(self, repo_slug=None, dir='/'):
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        dir = dir.lstrip('/')
        url = self.bitbucket.url(
            action='GET_ARCHIVE',
            username=self.bitbucket.username,
            repo_slug=repo_slug,
            format='src')
        dir_url = url + dir
        response = self.bitbucket.dispatch('GET', dir_url, auth=self.bitbucket.auth)
        if response[0] and isinstance(response[1], dict):
            repo_tree = response[1]
            url = self.bitbucket.url(
                action='GET_ARCHIVE',
                username=self.bitbucket.username,
                repo_slug=repo_slug,
                format='raw')
            # Download all files in dir
            for file in repo_tree['files']:
                file_url = url + '/'.join((file['path'],))
                response = self.bitbucket.dispatch('GET', file_url, auth=self.bitbucket.auth)
                self.bitbucket.repo_tree[file['path']] = response[1]
            # recursively download in dirs
            for directory in repo_tree['directories']:
                dir_path = '/'.join((dir, directory))
                self._get_files_in_dir(repo_slug=repo_slug, dir=dir_path)

    def public(self, username=None):
        """ Returns all public repositories from an user.
            If username is not defined, tries to return own public repos.
        """
        username = username or self.bitbucket.username or ''
        url = self.bitbucket.url(action='GET_USER', username=username)
        response = self.bitbucket.dispatch('GET', url)
        try:
            return (response[0], response[1]['repositories'])
        except TypeError:
            pass
        return response

    def all(self):
        """ Return own repositories."""
        data = {}
        url = self.bitbucket.url(action='GET_ALL', username=self.bitbucket.username)
        while url:
            response = self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)
            for repo in response[1]['values']:
                if repo['uuid'] not in data:
                    data[repo['uuid']] = repo
            url = response[1].get('next', None)
        return data

    def projects(self):
        """ Return own projects."""
        data = {}
        url = self.bitbucket.url(action='GET_ALL', username=self.bitbucket.username)
        while url:
            response = self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)
            for repo in response[1]['values']:
                if repo['project']['key'] not in data:
                    data[repo['project']['key']] = {
                        'key': repo['project']['key'],
                        'name': repo['project']['name']
                    }
            url = response[1].get('next', None)
        return data

    def get(self, repo_slug=None):
        """ Get a single repository on Bitbucket and return it."""
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='GET_REPO', username=self.bitbucket.username, repo_slug=repo_slug)
        return self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)

    def create(self, repo_slug, **kwargs):
        """ Creates a new repository on own Bitbucket account and return it."""
        url = self.bitbucket.url(action='CREATE_REPO', username=self.bitbucket.username, repo_slug=repo_slug)
        return self.bitbucket.dispatch('POST', url, auth=self.bitbucket.auth, **kwargs)

    def update(self, repo_slug=None, **kwargs):
        """ Updates repository on own Bitbucket account and return it."""
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='UPDATE_REPO', username=self.bitbucket.username, repo_slug=repo_slug)
        return self.bitbucket.dispatch('PUT', url, auth=self.bitbucket.auth, **kwargs)

    def delete(self, repo_slug=None):
        """ Delete a repository on own Bitbucket account.
            Please use with caution as there is NO confimation and NO undo.
        """
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='DELETE_REPO', username=self.bitbucket.username, repo_slug=repo_slug)
        return self.bitbucket.dispatch('DELETE', url, auth=self.bitbucket.auth)

    def archive(self, repo_slug=None, format='zip', prefix=''):
        """ Get one of your repositories and compress it as an archive.
            Return the path of the archive.

            format parameter is curently not supported.
        """
        prefix = '%s'.lstrip('/') % prefix
        self._get_files_in_dir(repo_slug=repo_slug, dir='/')
        if self.bitbucket.repo_tree:
            with NamedTemporaryFile(delete=False) as archive:
                with ZipFile(archive, 'w') as zip_archive:
                    for name, file in self.bitbucket.repo_tree.items():
                        with NamedTemporaryFile(delete=False) as temp_file:
                            temp_file.write(file.encode('utf-8'))
                        zip_archive.write(temp_file.name, prefix + name)
            return (True, archive.name)
        return (False, 'Could not archive your project.')

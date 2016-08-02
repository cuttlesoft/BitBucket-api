# -*- coding: utf-8 -*-
URLS = {
    # Get services (hooks)
    'GET_WEBHOOK': 'repositories/%(username)s/%(repo_slug)s/hooks/%(service_id)s/',
    'GET_WEBHOOKS': 'repositories/%(username)s/%(repo_slug)s/hooks/',
    # Set services (hooks)
    'SET_WEBHOOK': 'repositories/%(username)s/%(repo_slug)s/hooks/',
    'UPDATE_WEBHOOK': 'repositories/%(username)s/%(repo_slug)s/hooks/%(service_id)s/',
    'DELETE_WEBHOOK': 'repositories/%(username)s/%(repo_slug)s/hooks/%(service_id)s/',
}


class Webhook(object):
    """ This class provide services-related methods to Bitbucket objects."""

    def __init__(self, bitbucket):
        self.bitbucket = bitbucket
        self.bitbucket.URLS.update(URLS)

    def create(self, service, repo_slug=None, **kwargs):
        """ Add a service (hook) to one of your repositories.
            Each type of service require a different set of additionnal fields,
            you can pass them as keyword arguments (fieldname='fieldvalue').
        """
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='SET_WEBHOOK', username=self.bitbucket.username, repo_slug=repo_slug)
        kwargs['type'] = service
        # dumb.
        return self.bitbucket.dispatch('POST', url, auth=self.bitbucket.auth, dump_json=True, **kwargs)

    def get(self, service_id, repo_slug=None):
        """ Get a service (hook) from one of your repositories."""
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='GET_WEBHOOK', username=self.bitbucket.username, repo_slug=repo_slug, service_id=service_id)
        return self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)

    def update(self, service_id, repo_slug=None, **kwargs):
        """ Update a service (hook) from one of your repositories.
        """
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='UPDATE_WEBHOOK', username=self.bitbucket.username, repo_slug=repo_slug, service_id=service_id)
        return self.bitbucket.dispatch('PUT', url, auth=self.bitbucket.auth, **kwargs)

    def delete(self, service_id, repo_slug=None):
        """ Delete a service (hook) from one of your repositories.
            Please use with caution as there is NO confimation and NO undo.
        """
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='DELETE_WEBHOOK', username=self.bitbucket.username, repo_slug=repo_slug, service_id=service_id)
        return self.bitbucket.dispatch('DELETE', url, auth=self.bitbucket.auth)

    def all(self, repo_slug=None):
        """ Get all services (hook) from one of your repositories.
        """
        repo_slug = repo_slug or self.bitbucket.repo_slug or ''
        url = self.bitbucket.url(action='GET_WEBHOOKS', username=self.bitbucket.username, repo_slug=repo_slug)
        return self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)

#  ============
#  = Services =
#  ============
# WEBHOOKS = {
#   'Basecamp': ('Username', 'Password', 'Discussion URL',),
#   'CIA.vc': ('Module', 'Project',),
#   'Email Diff': ('Email',),
#   'Email': ('Email',),
#   'FogBugz': ('Repository ID', 'CVSSubmit URL',),
#   'FriendFeed': ('Username', 'Remote Key', 'Format',),
#   'Geocommit': (None,),
#   'Issues': (None,),
#   'Lighthouse': ('Project ID', 'API Key', 'Subdomain',),
#   'Pivotal Tracker': ('Token',),
#   'POST': ('URL',),
#   'Rietveld': ('Email', 'Password', 'URL',),
#   'Superfeedr': (None,),
# }

import logging

log = logging.getLogger(__name__)

class ApiModelManager():
    def __init__(self, api):
        self.api = api

        # Required subclass properties
        if type(self.model_name)        is not str: raise NotImplementedError()
        if type(self.model_name_plural) is not str: raise NotImplementedError()

    def list_all(self, embed=[]):
        qs = ('?embed=' + ','.join(embed)) if embed else ''
        return self.api.http_get_result(f'/{self.model_name}/list/{qs}', ensure_status=[200])

    def read(self, uuid, embed=[]):
        qs = ('?embed=' + ','.join(embed)) if embed else ''
        return self.api.http_get_result(f'/{self.model_name}/read/{uuid}{qs}', ensure_status=[200])

    def create(self, tocreate, wait=True):
        """
        Create the given items
        If wait=True, blocks until all are ready
        """
        created = []
        if not tocreate: return created
        log.info(f'Creating {self.model_name_plural}: {repr(tocreate)}')
        created += self.api.http_post_result(f'/{self.model_name}/create/', tocreate, ensure_status=[200])
        if wait and not self.is_instantaneous:
            self.api.wait_ready(self.model_name, [item[self.primary_key] for item in created])
        return created

    def create_one(self, tocreate, wait=True):
        """
        Create the given item
        If wait=True, blocks until ready
        """
        created = self.create([tocreate], wait=wait)
        assert len(created) == 1
        return created[0]

    def update(self, toupdate, wait=True):
        """
        Update the given items
        If wait=True, blocks until all are ready
        """
        updated = []
        if not toupdate: return updated
        log.info(f'Updating {self.model_name_plural}: {repr(toupdate)}')
        updated += self.api.http_post_result(f'/{self.model_name}/update/', toupdate, ensure_status=[200])
        if wait and not self.is_instantaneous:
            self.api.wait_ready(self.model_name, [item[self.primary_key] for item in updated])
        return updated

    def update_one(self, toupdate, wait=True):
        """
        Update the given item
        If wait=True, blocks until ready
        """
        updated = self.update([toupdate], wait=wait)
        assert len(updated) == 1
        return updated[0]

    def delete(self, todelete, wait=True):
        """
        Delete the given items
        If wait=True, blocks until all are deleted
        """
        if not todelete: return
        log.info(f'Deleting {self.model_name_plural}: {repr(todelete)}')
        self.api.http_post_result(f'/{self.model_name}/delete/', [{self.primary_key: item[self.primary_key]} for item in todelete], ensure_status=[200])
        if wait and not self.is_instantaneous:
            self.api.wait_deleted(self.model_name, [item[self.primary_key] for item in todelete])

    def delete_one(self, todelete, wait=True):
        """
        Delete the given items
        If wait=True, blocks until all are deleted
        """
        self.delete([todelete], wait=wait)

    # -- Equality, Obstruction, and Satisfaction --
    #
    # check_equals()    returns True iff the given definitions are effectively equivalent
    # check_obstructs() returns True iff the given "existing" definition obstructs the creation of the "new" one
    # check_satisfies() returns True iff the given "existing" definition satisfies the needs of the "new" one
    #
    # This is a strategy pattern. It is intended to override these methods to apply an Ensure policy.
    #
    # For example, apps are normally considered to be in conflict if they would have the same name under the same osuser.
    # It is fine to have two apps of the same name under different osusers.
    #
    # However, suppose we want to ensure application names are globally unique under an account.
    # We can accomplish this by changing the policy to consider the app name only:
    #
    #     def name_equals(this, a, b):
    #         return a['name'] == b['name']
    #
    #     def equal_obstructs(this, existing, new):
    #         return this.check_equals(new, existing)
    #
    #     def nothing_satisfies(this, existing, new):
    #         return False
    #
    #     import types
    #     opalapi = opalstack.Api(...)
    #     opalapi.apps.check_equals = types.MethodType(name_equals, opalapi.apps)
    #     opalapi.apps.check_obstructs = types.MethodType(equal_obstructs, opalapi.apps)
    #     opalapi.apps.check_satisfies = types.MethodType(nothing_satisfies, opalapi.apps)
    #
    # Another use case would be to modify the database user policy to not consider
    # existing users for satisfaction. By default, an existing database user of
    # the requested name and server will be retained as satisfying the needs of the request.
    # This is reasonable default behavior, but in the case where the that dbuser's
    # password is unknown, you may want to consider the existing dbuser as obstructing
    # rather than satisfying.
    #
    def check_equals(self, a, b):             raise NotImplementedError()
    def check_obstructs(self, existing, new): raise NotImplementedError()
    def check_satisfies(self, existing, new): raise NotImplementedError()

    def set_has(self, X, z):
        return any(self.check_equals(x, z) for x in X)

    def set_reduced(self, X):
        ret = []
        [ret.append(x) for x in X if not self.set_has(ret, x)]
        return ret

    def set_add(self, X, y):
        if not self.set_has(X, y): X.append(y)

    def set_remove(self, X, y):
        [X.remove(x) for x in X if self.check_equals(x, y)]

    def set_move(self, i, X, Y):
        self.set_remove(X, i)
        self.set_add(Y, i)

    def check_ensure(self, needed, purge=False):
        """
        Given a list of existing items and a list of needed items, produce three lists
        of operations which would collectively result in the desired state:
            toretain : a list of existing items that should be retained
            todelete : a list of existing items that must be deleted
            tocreate : a list of new items that must be created
        The optional parameter purge makes the final state exactly equal to the needed items,
            except that a new item will not replace an existing item that satisfies it.
        See also create(), delete(), and ensure(). These functions can be used to enforce state produced by this one.
        """
        assert type(needed) is list
        assert type(purge) is bool

        existing = self.list_all()

        def is_valid(items):
            """Check that no items in a set obstruct any other members in the same set"""
            for a in items:
                for b in items:
                    if a != b and self.check_obstructs(b, a): return False
            return True

        assert is_valid(existing)
        assert is_valid(needed)

        toretain = existing[:]
        todelete = []
        tocreate = []

        # Eliminate self-satisfied items
        satisfied = []
        for x in toretain:
            for y in toretain:
                if x != y and self.check_satisfies(y, x): self.set_add(satisfied, x)
        for item in satisfied:
            self.set_move(item, toretain, todelete)

        for a in needed:
            # Remove existing items if they obstruct or are obstructed by anything needed
            for b in toretain:
                if (    self.check_obstructs(a, b)
                     or self.check_obstructs(b, a) ): self.set_move(b, toretain, todelete)

            # Add any unsatisfied items to those which must exist
            for b in toretain:
                if self.check_satisfies(b, a): break
            else:
                self.set_add(tocreate, a)

        # Purge removes unneeded existing items
        if purge:
            trash = []
            for b in toretain:
                for a in needed:
                    if self.check_satisfies(b, a): break
                else:
                    self.set_add(trash, b)

            [self.set_move(item, toretain, todelete) for item in trash]

        return toretain, todelete, tocreate

    def ensure(self, needed, purge=False, wait=True):
        """
        Ensure the given items exist exactly as specified (modifying existing ones if necessary)
        This MAY delete existing items and create new ones in their place!
        If wait=True, blocks until created are ready
        """
        toretain, todelete, tocreate = self.check_ensure(needed, purge=purge)
        self.delete(todelete, wait=True)
        created = self.create(tocreate, wait=wait)
        return created

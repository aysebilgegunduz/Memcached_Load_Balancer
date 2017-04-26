import pylibmc


class Cache:
    def __init__(self, address):
        address = [address]
        self.client = pylibmc.Client(address)

        if self.client.get("total_hit") is None:
            # That means I am going to create users. Create total_hit
            # so I can increase it on each self.get_user() call
            self.client.add("total_hit", 0)

    def create_user(self, user_id, name, hit=None):
        """
        Create user at cache server.
        I am also using hit value if i move user from different cache server.
        :param user_id:
        :param name:
        :param hit:
        :return:
        """
        self.client.add(
            "user_{0}".format(user_id),
            name
        )
        # Not new user. i am just moving it another cache server.
        if hit is None:
            hit = 0

        self.client.add(
            "user_hit_{0}".format(user_id),
            int(hit)
        )

    def get_user(self, user_id, trigger_inc=True):
        """
        Return first name of given user id
        :param user_id:
        :param trigger_inc:
        :return:
        """
        name = self.client.get("user_{0}".format(user_id))
        if isinstance(name, str) and trigger_inc:
            self.increase_user_hit(user_id)
            self.increase_total_hit()
        return name

    def destroy(self, user_id):
        """
        Delete everything associated with given user.
        :param user_id:
        :return:
        """
        try:
            self.client.delete("user_{0}".format(user_id))
            self.client.delete("user_hit_{0}".format(user_id))
        except pylibmc.NotFound:
            return False
        return True

    def get_user_hit(self, user_id):
        """
        Return hit number of given user
        :param user_id:
        :return:
        """
        return self.client.get("user_hit_{0}".format(user_id))

    def get_total_hit(self):
        """
        Return the number of request processed by memcache.
        :return:
        """
        # i am using Cache class first time, we need to set total hit number to 0.
        return self.client.get("total_hit")

    def increase_total_hit(self):
        """
        Add +1 to the load number.
        :return:
        """
        self.client.incr("total_hit")

    def decrease_total_hit(self, n):
        """
        asd
        :param n:
        :return:
        """
        self.client.decr("total_hit", int(n))

    def increase_user_hit(self, user_id):
        """
        Increase hit number of given user.
        :param user_id:
        :return:
        """
        self.client.incr("user_hit_{0}".format(user_id))

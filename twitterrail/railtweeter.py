from datetime import datetime

emoji_skull = "\xF0\x9F\x92\x80"
emoji_tick = "\xE2\x9C\x94"
emoji_cross = "\xE2\x9C\x96"
emoji_train = "\xF0\x9F\x9A\x84"
emoji_late = "\xF0\x9F\x95\x93"


class RailTweeter:
    def __init__(self, tweeter, queries, home, work, users):
        self.tweeter = tweeter
        self.queries = queries
        self.home = home
        self.work = work
        self.users = users.split(",")
        self.last_message = ""

    def do_it(self):
        now = datetime.now()
        if now.hour < 12:
            origin = self.home
            destination = self.work
        else:
            origin = self.work
            destination = self.home

        services = list(self.queries.services_between(origin, destination))

        self.direct_messages(services, now)
        self.tweet_digest(services, origin, destination)

    @staticmethod
    def get_emoji(ser):
        if ser["etd"].lower() == "cancelled":
            return emoji_cross
        if ser["etd"].lower() == "on time":
            return emoji_tick
        else:
            return emoji_late

    @staticmethod
    def etd_str(ser):
        if ser["etd"].lower() == "cancelled" or ser["etd"].lower() == "on time":
            return ""
        else:
            return " {0}".format(ser["etd"])

    @staticmethod
    def platform_str(ser):
        if ser["platform"] != "-":
            return " P{0}".format(ser["platform"])
        else:
            return ""

    @staticmethod
    def destination_str(ser):
        return ser["destination"][:10].strip()

    def tweet_digest(self, services, origin, destination):
        lines = map(lambda ser: "{0} {1} {2}{3}{4}".format(self.get_emoji(ser),
                                                         ser["std"],
                                                         self.destination_str(ser),
                                                         self.etd_str(ser),
                                                         self.platform_str(ser)),
                    services)

        message = "{0} {1} - {2}: \n".format(emoji_train, origin, destination)

        if len(lines) == 0:
            message += "\nNo services"

        for line in lines:
            if len(message) + len(line) > 140:
                break
            message = message + "\n" + line

        self.send_tweet(message)

    @staticmethod
    def messages_allowed_at_this_time(now):
        return now.weekday() < 5 and 6 <= now.hour < 22

    def direct_messages(self, services, now):
        if self.messages_allowed_at_this_time(now):
            self.process_cancellations(services)
            self.process_late_trains(services)

    @staticmethod
    def time_to_mins(time_str):
        try:
            splits = time_str.split(":")
            h = int(splits[0])
            m = int(splits[1])
            return (h * 60) + m
        except:
            return -1

    def process_late_trains(self, services):
        late_trains = filter(lambda x: x["etd"].lower() != x["std"].lower()
                                       and x["etd"].lower() != "on time"
                                       and x["etd"].lower() != "cancelled"
                                       and x["etd"].lower() != "delayed", services)
        for service in late_trains:
            std = self.time_to_mins(service["std"])
            etd = self.time_to_mins(service["etd"])

            if etd > 0 and std > 0 and etd - std >= 15:
                message = "{0} {1} from {2} to {3} delayed expected {4}".format(
                        emoji_late,
                        service["std"],
                        service["origin"],
                        service["destination"],
                        service["etd"]
                )
                self.send_dm(message)

    def process_cancellations(self, services):
        cancellations = filter(lambda x: x["etd"].lower() == "cancelled", services)

        for service in cancellations:
            message = "{0} {1} from {2} to {3} has been cancelled".format(
                    emoji_skull,
                    service["std"],
                    service["origin"],
                    service["destination"]
            )
            self.send_dm(message)

    # Duplicate tweets are less annoying than duplicate messages, so are handled in a much more simple manner
    # The twitter API itself picks up the duplicate if one sneaks past here.
    def send_tweet(self, message):
        if message != self.last_message:
            print message
            self.last_message = message
            self.tweeter.tweet(message)

    def send_dm(self, message):
        for user in self.users:
            sent_messages = self.tweeter.messages_sent_to(user)
            previous = filter(
                    lambda msg: msg["message"] == message and
                                (datetime.now() - msg["timestamp"]).days < 1,
                    sent_messages
            )
            if len(previous) > 0:
                print "Identical message sent to {0} already today".format(user)
            else:
                print "Messaging {0}".format(user)
                self.tweeter.message(user, message)

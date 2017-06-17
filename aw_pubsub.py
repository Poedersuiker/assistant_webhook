from google.cloud import pubsub


class AWPubSub:
    def __init__(self):
        self.topics = {}

    def publish_msg(self, project, topic, msg):
        if self.check_project(project):
            if self.check_topic(project, topic):
                msg_id = self.topics[project][topic].publish(msg)
                return msg_id
            else:
                return 400
        else:
            return 400

    def check_project(self, project):
        if project in self.topics:
            return True
        else:
            try:
                self.topics[project] = pubsub.Client(project)
                return True
            except:
                return False

    def check_topic(self, project, topic):
        if topic in self.topics[project]:
            return True
        else:
            try:
                self.topics[project][topic] = self.topics[project].topic(topic)
                return True
            except:
                return False


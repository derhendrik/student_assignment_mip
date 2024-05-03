import json
from types import SimpleNamespace

import gurobipy as gp
from gurobipy import GRB


class Student:
    def __init__(self, unique_id, preferences):
        self.unique_id = unique_id
        self.preferences = preferences
        self.preferences_dict = {index + 1: elem for index, elem in enumerate(preferences)}
        self.assigned_topic = None

    def __repr__(self):
        return "Studi_" + str(self.unique_id)


class Group:
    def __init__(self, unique_id, preferences, size):
        self.unique_id = unique_id
        self.preferences = preferences
        self.preferences_dict = {index + 1: elem for index, elem in enumerate(preferences)}
        self.size = size
        self.assigned_topic = None

    def __repr__(self):
        return "Group_" + str(self.unique_id)


class Supervisor:
    def __init__(self, unique_id, topic_ids, min_topics, max_topics):
        self.unique_id = unique_id
        self.topic_ids = topic_ids
        self.min_topics = min_topics
        self.max_topics = max_topics

    def __repr__(self):
        return "Superv_" + str(self.unique_id)


def read_data():
    f = open('data/students.json')
    students = json.load(f, object_hook=lambda d: SimpleNamespace(**d)).students

    f = open('data/groups.json')
    groups = json.load(f, object_hook=lambda d: SimpleNamespace(**d)).groups

    f = open('data/supervisors.json')
    supervisors = json.load(f, object_hook=lambda d: SimpleNamespace(**d)).supervisors

    topics = [_ for supervisor in supervisors for _ in supervisor.topic_ids]
    assert topics == list(range(min(topics), max(topics) + 1))

    students = [Student(_.id, _.preferences) for _ in students]
    groups = [Group(_.id, _.preferences, _.size) for _ in groups]
    supervisors = [Supervisor(_.id, _.topic_ids, _.min_topics, _.max_topics) for _ in supervisors]

    for student in students:
        for topic in topics:
            assert topic in student.preferences

    return students, groups, supervisors, topics


def optimize(students, groups, supervisors, topics):
    model = gp.Model()

    # TODO: set a model parameter so that a log-file is produced and saved as "my_log_file"
    #

    x_st_students = model.addVars(students, topics, vtype=GRB.BINARY, name="x_st_students")

    # TODO: create the binary variables "x_gt_students"
    #

    modes = [1, 2]
    y_tm = model.addVars(topics, modes, vtype=GRB.BINARY, name="topic_mode")

    model.setObjective(gp.quicksum(
        student.preferences_dict[topic] ** 2 * x_st_students[student, topic] for student in students for topic in
        topics) + gp.quicksum(
        group.preferences_dict[topic] ** 2 * group.size * x_gt_groups[group, topic] for group in groups for topic in
        topics), GRB.MINIMIZE)

    model.addConstrs(
        constrs=(gp.quicksum(x_st_students[student, topic] for topic in topics) == 1 for student in students),
        name="exactly_one_topic_per_student")

    # TODO: add the constraints to the model such that exactly one topic is assigned per group
    #

    for supervisor in supervisors:
        model.addConstr(gp.quicksum(
            y_tm[topic, mode] for topic in supervisor.topic_ids for mode in modes) >= supervisor.min_topics,
                        name="min_topics_supervisor")

        # TODO: add the constraint to the model such that the maximum number of topics for a supervisor is not exceeded
        #

    model.addConstrs(constrs=(gp.quicksum(y_tm[topic, mode] for mode in modes) <= 1 for topic in topics),
                     name="max_one_mode_per_topic")

    # TODO: add the constraints to the model such that only a single topic is assigned in "three-people-mode" (mode: 2)
    #

    # TODO: add the constraints to the model such that for each topic, the number of assigned student (last constraint on slides)

    model.addConstrs(constrs=(gp.quicksum(x_st_students[student, topic] for student in students) + gp.quicksum(
        group.size * x_gt_groups[group, topic] for group in groups) == gp.quicksum(
        (1 + mode) * y_tm[topic, mode] for mode in modes) for topic in topics), name="used topics - number of students balance constraint")


    # TODO: write the optimization model to a file called "assignment.lp"
    #
    model.optimize()

    epsilon = 0.0001

    print("\n#########   Solution Report   ###########\n")
    print("Student Assignment \n")
    for student in students:
        for topic in topics:
            if x_st_students[student, topic].X >= 1 - epsilon:
                print("Student {} assigned to topic {}. Rank of topic: {}".format(student.unique_id, topic,
                                                                                  student.preferences_dict[topic]))
                student.assigned_topic = topic

    print("\n")
    print("Group Assignment \n")
    for group in groups:
        for topic in topics:
            if x_gt_groups[group, topic].X >= 1 - epsilon:
                print("Group {} assigned to topic {}. Rank of topic: {}".format(group.unique_id, topic,
                                                                                group.preferences_dict[topic]))
                group.assigned_topic = topic

    print("################## FINISHED ##################")


def write_results(students, groups):
    with open('assignment_results.txt', 'w') as f:
        # TODO write a couple of lines of code that store the assigned topics (for groups and students) in a text-file
        # you can simply use f.write("....")


def assign_students():
    students, groups, supervisors, topics = read_data()
    optimize(students, groups, supervisors, topics)
    write_results(students, groups)


if __name__ == '__main__':
    assign_students()

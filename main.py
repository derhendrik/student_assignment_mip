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
    model.setParam("LogFile", "my_log_file")

    x_st_students = model.addVars(students, topics, vtype=GRB.BINARY, name="x_st_students")
    x_gt_groups = model.addVars(groups, topics, vtype=GRB.BINARY, name="x_gt_groups")

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

    model.addConstrs(constrs=(gp.quicksum(x_gt_groups[group, topic] for topic in topics) == 1 for group in groups),
                     name="exactly_one_topic_per_group")

    for supervisor in supervisors:
        model.addConstr(gp.quicksum(
            y_tm[topic, mode] for topic in supervisor.topic_ids for mode in modes) >= supervisor.min_topics,
                        name="min_topics_supervisor")
        model.addConstr(gp.quicksum(
            y_tm[topic, mode] for topic in supervisor.topic_ids for mode in modes) <= supervisor.max_topics,
                        name="max_topics_supervisor")

    model.addConstrs(constrs=(gp.quicksum(y_tm[topic, mode] for mode in modes) <= 1 for topic in topics),
                     name="max_one_mode_per_topic")

    model.addConstr(gp.quicksum(y_tm[topic, 2] for topic in topics) <= 1, name="limit_three-people-topics")

    model.addConstrs(constrs=(gp.quicksum(x_st_students[student, topic] for student in students) + gp.quicksum(
        group.size * x_gt_groups[group, topic] for group in groups) == gp.quicksum(
        (1 + mode) * y_tm[topic, mode] for mode in modes) for topic in topics), name="used topics - number of students balance constraint")

    model.write("assignment.lp")
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
        f.write("### Student Assignment ###")
        for student in students:
            f.write("\nStudent " + str(student.unique_id) + " assigned to topic " + str(student.assigned_topic))

        f.write("\n### Group Assignment ###")
        for group in groups:
            f.write("\nGroup " + str(group.unique_id) + " assigned to topic " + str(group.assigned_topic))


def assign_students():
    students, groups, supervisors, topics = read_data()
    optimize(students, groups, supervisors, topics)
    write_results(students, groups)


if __name__ == '__main__':
    assign_students()

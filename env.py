#!/usr/bin/env python

# -*- coding: utf-8 -*-

# author：Elan time:2020/1/9

from task import *
import copy as cp


class Env(object):
    def __init__(self):
        self.time = 0
        self.task_set = []
        self.instance = []
        self.no_processor = 0
        self.no_task = 0
        self.mean_deadline = 0
        self.mean_execute = 0
        self.mean_laxity = 0
        self.min_deadline = 0
        self.min_execute = 0
        self.min_laxity = 0
        self.saved = 0

    def reset(self):
        self.time = 0
        self.no_processor = 100
        self.no_task = 1000
        self.task_set = []
        self.instance = []
        for i in range(self.no_task):
            task = Task()
            self.task_set.append(task)
        self.update()
        self.saved = 0

    def step(self, actions):
        reward = np.zeros(len(self.instance))
        global_reward = 0
        done = np.zeros(len(self.instance))
        info = np.zeros(2)
        next_state = []
        # 对优先级排序，选前m个执行
        executable = np.argsort(actions)[-self.no_processor:]
        for i in range(len(self.instance)):
            execute = False
            instance = self.instance[i]
            if i in executable:
                execute = True
            result = instance.step(execute)
            next_state.append(self.observation(instance))
            if result == "miss":
                reward[i] -= 1
                global_reward -= 1
                instance.over = True
                done[i] = 1
                info[1] += 1
            elif result == "finish":
                reward[i] += 1
                info[0] += 1
                global_reward += 1
                instance.over = True
                done[i] = 1
        self.time += 1
        self.update()
        self.del_instance()
        return reward + global_reward, done, next_state, info

    def update(self):
        if len(self.instance) == 0:
            self.min_deadline = 0
            self.min_execute = 0
            self.min_laxity = 0
            self.mean_deadline = 0
            self.mean_execute = 0
            self.mean_laxity = 0
            return
        instance_deadline = []
        instance_execute = []
        instance_laxity = []
        for i in self.instance:
            instance_deadline.append(i.deadline)
            instance_execute.append(i.execute_time)
            instance_laxity.append(i.laxity_time)
        self.min_deadline = min(instance_deadline)
        self.min_execute = min(instance_execute)
        self.min_laxity = min(instance_laxity)
        self.mean_deadline = np.mean(instance_deadline)
        self.mean_execute = np.mean(instance_execute)
        self.mean_laxity = np.mean(instance_laxity)
        print(self.mean_deadline, self.mean_laxity)

    def arrive(self):
        for task in self.task_set:
            if self.time == task.arrive_time[task.count]:
                self.instance.append(task.create_instance())
        self.update()

    def done(self):
        if len(self.instance) > 0:
            return False
        for t in self.task_set:
            if t.count < FREQUENCY - 1:
                return False
        return True

    def observation(self, instance):
        return np.array([instance.execute_time - self.mean_execute, instance.deadline - self.mean_deadline,
                         instance.laxity_time - self.mean_laxity, instance.execute_time - self.min_execute,
                         instance.deadline - self.min_deadline, instance.laxity_time - self.min_laxity])

    def save(self):
        self.saved = cp.deepcopy(self.task_set)

    def load(self):
        self.time = 0
        self.instance = []
        self.task_set = self.saved
        self.update()

    def del_instance(self):
        for i in self.instance:
            if i.over:
                self.instance.remove(i)
                del i

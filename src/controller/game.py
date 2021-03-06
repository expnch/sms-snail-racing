import json
import random

class Game():
    def __init__(self, redis_client, goal=100, jitter=2, air_resistance=2, max_velocity=7, timer=5):
        self.client = redis_client
        self.goal = goal
        self.jitter = jitter
        self.timer = timer
        self.max_velocity = max_velocity
        self.air_resistance = air_resistance

        if self.client.exists('state'):
            self.state = self.client.get('state').decode('UTF-8')
        else:
            self.state = 'setup'
            self.client.set('state', 'setup')

        if self.client.exists('winners'):
            w = self.client.get('winners').decode('UTF-8')
            if w:
                self.winners = list(map(int, w.split(',')))
            else:
                self.winners = []
        else:
            self.winners = []
            self.client.set('winners', '')

        if self.client.exists('names'):
            self.names = json.loads(self.client.get('names').decode('UTF-8'))
        else:
            self.names = {'0': 'Wanda'
                         ,'1': 'Yorick'
                         ,'2': 'Zippy'
                         }
            self.client.set('names', json.dumps(self.names))
        self.snails = list(map(str, range(len(self.names))))

        if self.client.exists('position'):
            self.position = json.loads(self.client.get('position').decode('UTF-8'))
        else:
            self.position = {'0': 0
                            ,'1': 0
                            ,'2': 0
                            }
            self.client.set('position', json.dumps(self.position))

        if self.client.exists('velocity'):
            self.velocity = json.loads(self.client.get('velocity').decode('UTF-8'))
        else:
            self.velocity = {'0': 0
                            ,'1': 0
                            ,'2': 0
                            }
            self.client.set('velocity', json.dumps(self.velocity))

        if self.client.exists('countdown'):
            self.countdown = int(self.client.get('countdown').decode('UTF-8'))
        else:
            self.countdown = self.timer
            self.client.set('countdown', self.countdown)

    def process(self):
        if self.state == 'ready':
            self.client.publish('messages', json.dumps({'type': 'announcement', 'body': 'Race begins in {}'.format(self.countdown)}))
            if self.count():
                self.change_state()
        elif self.state == 'race':
            for k in self.snails:
                self.move_snail(k)
                if self.velocity[k] > 1:
                    r = self.air_resistance if self.velocity[k] - self.air_resistance >= 1 else self.velocity[k] - 1
                    r *= -1
                    self.change_velocity(k, amount=r)
                if self.position[k] >= self.goal:
                    self.winners.append(k)
            self.client.publish('messages', json.dumps({'type': 'move', 'body': ','.join([str(self.position[k]) for k in self.snails])}))
            if self.winners:
                self.client.set('winners', ','.join(map(str, self.winners)))
                self.change_state()
                self.client.publish('messages',
                                    json.dumps({'type': 'announcement-long',
                                                'body': '{} Win{}!!'.format(" and ".join([self.names[k] for k in self.winners]), '' if len(self.winners) > 1 else 's')}))
                
    def move_snail(self, snail_id, absolute=None):
        if absolute is not None:
            self.position[snail_id] = absolute 
        else:
            self.position[snail_id] += self.velocity[snail_id] + random.randint(0,self.jitter)
        self.client.set('position', json.dumps(self.position))

    def change_velocity(self, snail_id, amount=0, absolute=None):
        if absolute is not None:
            self.velocity[snail_id] = absolute
        else:
            self.velocity[snail_id] += amount
            if self.velocity[snail_id] > self.max_velocity:
                self.velocity[snail_id] = self.max_velocity
        self.client.set('velocity', json.dumps(self.velocity))

    def count(self):
        self.countdown -= 1
        self.client.set('countdown', self.countdown)
        if self.countdown == 0:
            return True
        return False

    def change_state(self, state=None):
        if state == 'ready' or self.state == 'setup':
            self.state = 'ready'
            self.countdown = self.timer
            self.client.set('countdown', self.countdown)
        elif state == 'race' or self.state == 'ready':
            self.state = 'race'
            for k in self.snails:
               self.change_velocity(k, absolute=1)
        elif state == 'victory' or self.state == 'race':
            self.state = 'victory'
        elif state == 'setup' or self.state == 'victory':
            self.state = 'setup'
            for k in self.snails:
                self.move_snail(k, absolute=0)
                self.change_velocity(k, absolute=0)
                self.winners = []
                self.client.set('winners', '')
            self.client.publish('messages', json.dumps({'type': 'move', 'body': ','.join([str(self.position[k]) for k in self.snails])}))

        self.client.set('state', self.state)
        self.publish_state()

    def publish_state(self):
        self.client.publish('messages', json.dumps({'type': 'state', 'body': self.state}))

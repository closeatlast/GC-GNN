from __future__ import print_function
import random
import numpy as np
from multiprocessing import Pool
import time
from collections import OrderedDict

def deepwalk_walk_wrapper(class_instance, walk_length, start_node):
    class_instance.deepwalk_walk(walk_length, start_node)

#deepwalk
class BasicWalker:
    def __init__(self, G, workers,walk_length):
        self.G = G.G
        self.node_size = G.node_size
        self.look_up_dict = G.look_up_dict
        self.walk_length=walk_length
    def deepwalk_walk(self, start_node):#original
        '''
        Simulate a random walk starting from start node.
        '''
        G = self.G
        walk = [start_node]

        while len(walk) < self.walk_length:
            cur = walk[-1]
            cur_nbrs = list(G.neighbors(cur))
            if len(cur_nbrs) > 0:
                walk.append(random.choice(cur_nbrs))
            else:
                break
        return walk
    
    def deepwalk_walk_weighted(self, start_node):#our weighted
        '''
        Simulate a random walk starting from start node.
        '''
        G = self.G
        alias_nodes = self.alias_nodes
        walk = [start_node]

        while len(walk) < self.walk_length:
            cur = walk[-1]
            cur_nbrs = list(G.neighbors(cur))
            if len(G[cur]) > 0:
                walk.append(cur_nbrs[alias_draw(alias_nodes[cur][0], alias_nodes[cur][1])])
            else:
                break
        return walk

    def simulate_walks(self, num_walks, walk_length,tri=False):
        '''
        Repeatedly simulate random walks from each node.
        '''
        G = self.G
        walks = []
        nodes = list(G.nodes())
#        print('Walk iteration:')
        node_size = len(nodes)

        for walk_iter in range(num_walks):
            random.shuffle(nodes)
#            pool = multiprocessing.Pool(processes = 4)
#            walksit = pool.map(self.deepwalk_walk, nodes  )
#            walks.extend(walksit)
            for node in nodes:
#                print(node)
                walks.append(self.deepwalk_walk_weighted(start_node=node))
#                walks.append(self.deepwalk_walk(start_node=node))
        # print(len(walks))
        return walks

    def preprocess_transition_probs(self):
        '''
        Preprocessing of transition probabilities for guiding the random walks.
        '''
        G = self.G
        t1 = time.time() 
        alias_nodes = {}
        for node in G.nodes():
            unnormalized_probs = [G[node][nbr]['weight'] for nbr in G.neighbors(node)]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
            alias_nodes[node] = alias_setup(normalized_probs)
        self.alias_nodes = alias_nodes
    #node2vec
class Walker:
    def __init__(self, G, p, q, workers):
        self.G = G.G
        self.p = p
        self.q = q
        self.node_size = G.node_size
        self.look_up_dict = G.look_up_dict
        self.notriangle=0.001

    def node2vec_walk(self, walk_length, start_node):
        '''
        Simulate a random walk starting from start node.
        '''
        G = self.G
        alias_nodes = self.alias_nodes
        alias_edges = self.alias_edges

        walk = [start_node]

        while len(walk) < walk_length:
            cur = walk[-1]
            cur_nbrs = sorted(G.neighbors(cur))
            if len(cur_nbrs) > 0:
                if len(walk) == 1:
                    walk.append(
                        cur_nbrs[alias_draw(alias_nodes[cur][0], alias_nodes[cur][1])])
                else:
                    prev = walk[-2]
                    pos = (prev, cur)
#                    if pos not in alias_edges:
#                        pos = (cur, prev)
#                    print(pos)
                    next = cur_nbrs[alias_draw(alias_edges[pos][0],
                                               alias_edges[pos][1])]
                    walk.append(next)
            else:
                break

        return walk
    

    
    def simulate_walks(self, num_walks, walk_length,tri=False):
        '''
        Repeatedly simulate random walks from each node.
        '''
        G = self.G
        walks = []
        nodes = list(G.nodes())
#        print('Walk iteration:')
        for walk_iter in range(num_walks):
#            print(str(walk_iter+1), '/', str(num_walks))
            random.shuffle(nodes)
            for node in nodes:
#                if tri:
#                    walks.append(self.triangle_walk2(
#                            walk_length=walk_length, start_node=node))
#                else:
                    walks.append(self.node2vec_walk(
                            walk_length=walk_length, start_node=node))

        return walks

    def get_alias_edge(self, e):
        '''
        Get the alias edge setup lists for a given edge.
        '''
        (src, dst)=e
        G = self.G
        p = self.p
        q = self.q

        unnormalized_probs = []
        for dst_nbr in sorted(G.neighbors(dst)):
            if dst_nbr == src:
                unnormalized_probs.append(G[dst][dst_nbr]['weight']/p)
            elif G.has_edge(dst_nbr, src):
                unnormalized_probs.append(G[dst][dst_nbr]['weight'])
            else:
                unnormalized_probs.append(G[dst][dst_nbr]['weight']/q)
        norm_const = sum(unnormalized_probs)
        normalized_probs = [
            float(u_prob)/norm_const for u_prob in unnormalized_probs]

        return alias_setup(normalized_probs)

   

    def preprocess_transition_probs(self):
        '''
        Preprocessing of transition probabilities for guiding the random walks.
        '''
        G = self.G
        t1 = time.time() 
        alias_nodes = {}
        for node in G.nodes():
            unnormalized_probs = [G[node][nbr]['weight'] for nbr in G.neighbors(node)]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
            alias_nodes[node] = alias_setup(normalized_probs)
        t2 = time.time()   
#        print(t2-t1)
        alias_edges = {}
        triads = {}
#        print("finish pro1")
        node_size = self.node_size
        i=0
        t1 = time.time()  
        for edge in G.edges():
#            if i%10000==0:
#                print(i)
#            i=i+1
#            re=(edge[1], edge[0])
#            if  re not in alias_edges:
                gae = self.get_alias_edge(edge)
                alias_edges[edge]=gae
#                alias_edges[re]=gae
        t2 = time.time()   
#        print(t2-t1)
        self.alias_nodes = alias_nodes
        self.alias_edges = alias_edges
#        print("finish pro")
        return

    def preprocess_transition_probs_par(self):
        '''
        Preprocessing of transition probabilities for guiding the random walks.
        '''
        G = self.G

        nl=G.nodes()
        t1 = time.time() 
        alias_nodes = {}
        
        for node in G.nodes():
            unnormalized_probs = [G[node][nbr]['weight'] for nbr in G.neighbors(node)]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
            alias_nodes[node] = alias_setup(normalized_probs)
        self.alias_nodes=alias_nodes
        t2 = time.time()   
        print(t2-t1)
        t1 = time.time() 
        with Pool(processes=40) as pool:         # start 4 worker processes
            alias_edges = pool.map(self.get_alias_edge, G.edges()  )
        self.alias_edges = dict(zip(G.edges() , alias_edges))
        t2 = time.time()   
        print(t2-t1)
#        print("finish pro")
        return
    def get_alias_node_par(self,node):
        G = self.G
        unnormalized_probs = [G[node][nbr]['weight'] for nbr in G.neighbors(node)]
        norm_const = sum(unnormalized_probs)
        normalized_probs = [float(u_prob)/norm_const for u_prob in unnormalized_probs]
        alias_node = alias_setup(normalized_probs)
        return alias_node


def alias_setup(probs):
    '''
    Compute utility lists for non-uniform sampling from discrete distributions.
    Refer to https://hips.seas.harvard.edu/blog/2013/03/03/the-alias-method-efficient-sampling-with-many-discrete-outcomes/
    for details
    '''
    K = len(probs)
    q = np.zeros(K, dtype=np.float32)
    J = np.zeros(K, dtype=np.int32)

    smaller = []
    larger = []
    for kk, prob in enumerate(probs):
        q[kk] = K*prob
        if q[kk] < 1.0:
            smaller.append(kk)
        else:
            larger.append(kk)

    while len(smaller) > 0 and len(larger) > 0:
        small = smaller.pop()
        large = larger.pop()

        J[small] = large
        q[large] = q[large] + q[small] - 1.0
        if q[large] < 1.0:
            smaller.append(large)
        else:
            larger.append(large)

    return J, q


def alias_draw(J, q):
    '''
    Draw sample from a non-uniform discrete distribution using alias sampling.
    '''
    K = len(J)

    kk = int(np.floor(np.random.rand()*K))
    if np.random.rand() < q[kk]:
        return kk
    else:
        return J[kk]
def pick_random(prob_list):
  s=0
  r, s = random.random(), 0
  #print('r',r)
  for (k,v) in prob_list.items():
    s += v
    if s >= r:
      return k
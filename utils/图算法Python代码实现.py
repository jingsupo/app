# 图算法Python代码实现

import matplotlib.pyplot as plt
import networkx as nx


# 1、连通分量

"""
连通分量算法近似看作一种硬聚类算法，该算法旨在寻找相关数据的簇类。举一个具体的例子：假设拥有连接世界上任意城市的路网数据，我们需要找出世界上所有的大陆，以及它们所包含的城市。我们该如何实现这一目标呢？
基于BFS / DFS的连通分量算法能够达成这一目的，接下来，我们将用 Networkx 实现这一算法。
"""

# 首先创建边的列表，列表中每个元素包含两个城市的名称，以及它们之间的距离。

edgelist = [['Mannheim', 'Frankfurt', 85], ['Mannheim', 'Karlsruhe', 80], ['Erfurt', 'Wurzburg', 186], ['Munchen', 'Numberg', 167], ['Munchen', 'Augsburg', 84], ['Munchen', 'Kassel', 502], ['Numberg', 'Stuttgart', 183], ['Numberg', 'Wurzburg', 103], ['Numberg', 'Munchen', 167], ['Stuttgart', 'Numberg', 183], ['Augsburg', 'Munchen', 84], ['Augsburg', 'Karlsruhe', 250], ['Kassel', 'Munchen', 502], ['Kassel', 'Frankfurt', 173], ['Frankfurt', 'Mannheim', 85], ['Frankfurt', 'Wurzburg', 217], ['Frankfurt', 'Kassel', 173], ['Wurzburg', 'Numberg', 103], ['Wurzburg', 'Erfurt', 186], ['Wurzburg', 'Frankfurt', 217], ['Karlsruhe', 'Mannheim', 80], ['Karlsruhe', 'Augsburg', 250],["Mumbai", "Delhi",400],["Delhi", "Kolkata",500],["Kolkata", "Bangalore",600],["TX", "NY",1200],["ALB", "NY",800]]

# 然后，使用 Networkx 创建图：

g = nx.Graph()
for edge in edgelist:
    g.add_edge(edge[0],edge[1], weight = edge[2])

# 现在，我们想从这张图中找出不同的大陆及其包含的城市。我们可以使用使用连通分量算法来执行此操作：

for i, x in enumerate(nx.connected_components(g)):
    print("cc"+str(i)+":",x)

# 从结果中可以看出，只需使用边缘和顶点，我们就能在数据中找到不同的连通分量。

# 2、最短路径

"""
继续上面的例子，我们拥有了德国的城市群及其相互距离的图表。为了计算从法兰克福前往慕尼黑的最短路径，我们需要用到 Dijkstra 算法。Dijkstra 是这样描述他的算法的：
从鹿特丹到格罗宁根的最短途径是什么？或者换句话说：从特定城市到特定城市的最短路径是什么？这便是最短路径算法，而我只用了二十分钟就完成了该算法的设计。 一天早上，我和未婚妻在阿姆斯特丹购物，我们逛累了，便在咖啡馆的露台上喝了一杯咖啡。而我，就想着我能够做到这一点，于是我就设计了这个最短路径算法。正如我所说，这是一个二十分钟的发明。事实上，它发表于1959年，也就是三年后。它之所以如此美妙，其中一个原因在于我没有用铅笔和纸张就设计了它。后来我才知道，没有铅笔和纸的设计的一个优点就是，你几乎被迫避免所有可避免的复杂性。最终，这个算法让我感到非常惊讶，而且也成为了我名声的基石之一。
——Edsger Dijkstra
于2001年接受ACM通讯公司 Philip L. Frana 的采访时的回答
"""

print(nx.shortest_path(g, 'Stuttgart','Frankfurt',weight='weight'))
print(nx.shortest_path_length(g, 'Stuttgart','Frankfurt',weight='weight'))

# 使用以下命令可以找到所有对之间的最短路径： 

for x in nx.all_pairs_dijkstra_path(g,weight='weight'):
    print(x)

# 3、最小生成树

"""
假设我们在水管工程公司或互联网光纤公司工作，我们需要使用最少的电线（或者管道）连接图表中的所有城市。我们如何做到这一点？
"""

# nx.minimum_spanning_tree(g) returns a instance of type graph
nx.draw_networkx(nx.minimum_spanning_tree(g))

"""
# 4、网页排序（Pagerank）

# reading the dataset
fb = nx.read_edgelist('../input/facebook-combined.txt', create_using = nx.Graph(), nodetype = int)

pos = nx.spring_layout(fb)

import warnings
warnings.filterwarnings('ignore')

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 15)
plt.axis('off')
nx.draw_networkx(fb, pos, with_labels = False, node_size = 35)
plt.show()

# 现在，我们想要找到具有高影响力的用户。直观上来讲，Pagerank 会给拥有很多朋友的用户提供更高的分数，而这些用户的朋友反过来会拥有很多朋友。

pageranks = nx.pagerank(fb)
print(pageranks)

# 使用如下代码，我们可以获取排序后 PageRank 值，或者最具有影响力的用户：

import operator
sorted_pagerank = sorted(pagerank.items(), key=operator.itemgetter(1),reverse = True)
print(sorted_pagerank)

# 将含有最具影响力用户的子图进行可视化：

first_degree_connected_nodes = list(fb.neighbors(3437))
second_degree_connected_nodes = []
for x in first_degree_connected_nodes:
    second_degree_connected_nodes+=list(fb.neighbors(x))
second_degree_connected_nodes.remove(3437)
second_degree_connected_nodes = list(set(second_degree_connected_nodes))
subgraph_3437 = nx.subgraph(fb,first_degree_connected_nodes+second_degree_connected_nodes)
pos = nx.spring_layout(subgraph_3437)
node_color = ['yellow' if v == 3437 else 'red' for v in subgraph_3437]
node_size =  [1000 if v == 3437 else 35 for v in subgraph_3437]
plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 15)
plt.axis('off')
nx.draw_networkx(subgraph_3437, pos, with_labels = False, node_color=node_color,node_size=node_size )
plt.show()

# 黄色的节点代表最具影响力的用户
"""

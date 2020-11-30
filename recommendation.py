import string
import re
import networkx
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from prettytable import PrettyTable

# RECOMMENDATIONS
#-----------------
print("Available groups\n")
print("1. Books\n")
print("2. Music\n")

val = input("Choose the group\n")
numberToGroupMapping = {
  "1": "amazon-books",
  "2": "amazon-music"
}

# key = ASIN; value = MetaData associated with ASIN
fhr = open(numberToGroupMapping[val]+".txt", 'r', encoding='utf-8', errors='ignore')
amazonProducts = {}
display = []
fhr.readline() #read first line and skip to second line 
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip()
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['Copurchased'] = cell[5].strip()
    MetaData['SalesRank'] = int(cell[6].strip())
    MetaData['TotalReviews'] = int(cell[7].strip())
    MetaData['AvgRating'] = float(cell[8].strip())
    display.append(cell[1].strip())
    amazonProducts[ASIN] = MetaData
fhr.close()

table = PrettyTable(['Product ID','Title','Average Rating', 'Total Reviews'])

for asin in np.random.choice(display, 15):
    table.add_row([asin, amazonProducts[asin]['Title'], amazonProducts[asin]['AvgRating'], amazonProducts[asin]['TotalReviews']])
  
print(table)


# Read the data from amazon-books-copurchase.edgelist and assign it to copurchaseGraph weighted Graph;
# node = ASIN; edge = copurchase, edge weight = category similarity
fhr = open(numberToGroupMapping[val]+"-copurchase.edgelist", "rb")
copurchaseGraph = networkx.read_weighted_edgelist(fhr)
fhr.close()

purchasedAsin = input('Enter your product id\n')

print("Looking for Recommendations for this Product:")
print("\n------------------------------------------------------------")

# Get the depth-1 ego network of purchasedAsin from copurchaseGraph
try:
    n = purchasedAsin
    ego = networkx.ego_graph(copurchaseGraph, n, radius=1)
    purchasedAsinEgoGraph = networkx.Graph(ego)
except: 
    print("No similar product available")
    exit()


# only retain edges with Threshold value
threshold = 0.2
purchasedAsinEgoTrimGraph = networkx.Graph()
purchasedAsinEgoTrimGraph.add_node(purchasedAsin)

for f,t,e in purchasedAsinEgoGraph.edges(data=True):
    if e['weight'] >= threshold:
        purchasedAsinEgoTrimGraph.add_edge(f,t, weight=e['weight'])

networkx.draw_networkx(purchasedAsinEgoTrimGraph)
plt.show()

for f,t,e in purchasedAsinEgoTrimGraph.edges(data=True):
    amazonProducts[t]['Similarity'] = e['weight']

# Get the list of nodes connected to the purchasedAsin
purchasedAsinNeighbours = purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)

# Get Top book recommendations from among the purchasedAsinNeighbours based on one or more of the following data of the 
# neighbouring nodes: AvgRating, TotalReviews

# Accessing metadata with ASIN in purchasedAsinNeighbours
AsMeta = []
for asin in purchasedAsinNeighbours:
    ASIN = asin
    Title = amazonProducts[asin]['Title']
    SalesRank = amazonProducts[asin]['SalesRank']
    TotalReviews = amazonProducts[asin]['TotalReviews']
    AvgRating = amazonProducts[asin]['AvgRating']
    Similarity = str(amazonProducts[asin]['Similarity']*100)+"%"
    AsMeta.append([ASIN, Title, AvgRating, TotalReviews, Similarity])
    
# Sorting the top five nodes in purchasedAsinNeighbour by Average Rating then by TotalReviews
T5_byAvgRating_then_byTotalReviews = sorted(AsMeta, key=lambda x: (x[3], x[2]), reverse=True)

# Print Top Recommendations
print('\nTop Recommendations by AvgRating then by TotalReviews for this Product:')
print('\n------------------------------------------------------------------------------------')
t = PrettyTable(['Product ID', 'Title', 'Average Ratimg', 'Total Reviews', 'Similarity'])
for asin in T5_byAvgRating_then_byTotalReviews:
    t.add_row(asin)

print(t)
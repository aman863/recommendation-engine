import string
import re
from stemming.porter2 import stem
import networkx

# PREPROCESSING
#----------------
fhr = open('amazon-meta.txt', 'r', encoding='utf-8', errors='ignore')# Reading input file
amazonProducts = {} #initialising an empty object

# Read data from amazon meta files and popoulate amazon products nested dictionary
(Id, ASIN, Title, Categories, Group, Copurchased, SalesRank, TotalReviews, AvgRating) = \
    ("", "", "", "", "", "", 0, 0, 0.0) # initialising values
for line in fhr:
    line = line.strip() #removing whitespaces
    # a product block started
    if(line.startswith("Id")):
        Id = line[3:].strip()
    elif(line.startswith("ASIN")):
        ASIN = line[5:].strip()
    elif(line.startswith("title")):
        Title = line[6:].strip()
        Title = ' '.join(Title.split())
        
    elif(line.startswith("group")):
        Group = line[6:].strip()
    elif(line.startswith("salesrank")):
        SalesRank = line[10:].strip()
    elif(line.startswith("similar")):
        ls = line.split()
        Copurchased = ' '.join([c for c in ls[2:]])
    elif(line.startswith("categories")):
        ls = line.split()
        Categories = ' '.join((fhr.readline()).lower() for i in range(int(ls[1].strip())))
        Categories = re.compile('[%s]' % re.escape(string.digits + string.punctuation)).sub(' ', Categories)
        Categories = ' '.join(set(Categories.split()) - set(stopwords.words("english")))
        Categories = ' '.join(stem(word) for word in Categories.split())
    elif(line.startswith("reviews")):
        ls = line.split()
        TotalReviews = ls[2].strip()
        AvgRating = ls[7].strip()
    # product block end
    # write out fields to amazonProducts dictionary
    elif(line==""):
        try:
            MetaData={}
            if(ASIN != ""):
                amazonProducts[ASIN] = MetaData
            MetaData['Id'] = Id
            MetaData['Title'] = Title
            MetaData['Categories'] = ' '.join(set(Categories.split()))
            MetaData['Group'] = Group
            MetaData['Copurchased'] = Copurchased
            MetaData['SalesRank'] = int(SalesRank)
            MetaData['TotalReviews'] = int(TotalReviews)
            MetaData['AvgRating'] = float(AvgRating)
            MetaData['DegreeCentrality'] = DegreeCentrality
            MetaData['ClusteringCoeff'] = ClusteringCoeff
        except NameError:
            continue
        (Id, ASIN, Title, Categories, Group, Copurchased, SalesRank, TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff) = \
            ("", "", "", "", "", "", 0, 0, 0.0, 0, 0.0)
fhr.close()

#create specific dictionaries
amazonBooks = {}
amazonMusic = {}
for asin,metadata in amazonProducts.items():
    if (metadata['Group']=='Book'):
        amazonBooks[asin] = amazonProducts[asin]
    elif(metadata['Group']=='Music'):
        amazonMusic[asin] = amazonProducts[asin]
    elif(metadata[asin]=='' )

# Write amazonBooks data to file
fhw = open('amazon-books.txt', 'w', encoding='utf-8', errors='ignore')
fhw.write("Id\t" + "ASIN\t" + "Title\t" + "Categories\t" + "Group\t" + "Copurchased\t" + "SalesRank\t" + "TotalReviews\t" + "AvgRating\n")
for asin, metadata in amazonBooks.items():
    fhw.write(metadata['Id'] + "\t" + \
              asin + "\t" + \
              metadata['Title'] + "\t" + \
              metadata['Categories'] + "\t" + \
              metadata['Group'] + "\t" + \
              metadata['Copurchased'] + "\t" + \
              str(metadata['SalesRank']) + "\t" + \
              str(metadata['TotalReviews']) + "\t" + \
              str(metadata['AvgRating']) + "\n")
fhw.close()

# Write amazonMusic data to file
fhw = open('amazon-music.txt', 'w', encoding='utf-8', errors='ignore')
fhw.write("Id\t" + "ASIN\t" + "Title\t" + "Categories\t" + "Group\t" + "Copurchased\t" + "SalesRank\t" + "TotalReviews\t" + "AvgRating\n")
for asin, metadata in amazonMusic.items():
    fhw.write(metadata['Id'] + "\t" + \
              asin + "\t" + \
              metadata['Title'] + "\t" + \
              metadata['Categories'] + "\t" + \
              metadata['Group'] + "\t" + \
              metadata['Copurchased'] + "\t" + \
              str(metadata['SalesRank']) + "\t" + \
              str(metadata['TotalReviews']) + "\t" + \
              str(metadata['AvgRating']) + "\n")
fhw.close()

# remove any copurchased items from copurchase list if we don't have metadata associated with it
for asin, metadata in amazonBooks.items():
    amazonBooks[asin]['Copurchased'] = \
        ' '.join([cp for cp in metadata['Copurchased'].split() \
                  if cp in amazonBooks.keys()])

for asin, metadata in amazonMusic.items():
    amazonMusic[asin]['Copurchased'] = \
        ' '.join([cp for cp in metadata['Copurchased'].split() \
                  if cp in amazonMusic.keys()])


# Create a product copurchase graph for analysis where the graph nodes for product ASINs
# and graph edge exists if two products were copurchased,
# with edge weight being a measure of category similarity between ASINs
    
copurchaseGraphBooks = networkx.Graph()
for asin,metadata in amazonBooks.items():
    copurchaseGraphBooks.add_node(asin)
    for a in metadata['Copurchased'].split():
        copurchaseGraphBooks.add_node(a.strip())
        similarity = 0
        n1 = set((amazonBooks[asin]['Categories']).split())
        n2 = set((amazonBooks[a]['Categories']).split())
        n1In2 = n1 & n2     # intersection (Number of words that are common between Categories of connected Nodes)
        n1Un2 = n1 | n2     # union (Total number of words in both Categories of connected Nodes)
        if(len(n1Un2)) > 0:
            similarity = round(len(n1In2)/len(n1Un2), 2)
        copurchaseGraphBooks.add_edge(asin, a.strip(), weight=similarity)

fhw = open('amazon-books-copurchase.edgelist', 'wb')
networkx.write_weighted_edgelist(copurchaseGraphBooks, fhw)
fhw.close()

copurchaseGraphMusic = networkx.Graph()
for asin,metadata in amazonMusic.items():
    copurchaseGraphMusic.add_node(asin)
    for a in metadata['Copurchased'].split():
        copurchaseGraphMusic.add_node(a.strip())
        similarity = 0
        n1 = set((amazonMusic[asin]['Categories']).split())
        n2 = set((amazonMusic[a]['Categories']).split())
        n1In2 = n1 & n2     # intersection (Number of words that are common between Categories of connected Nodes)
        n1Un2 = n1 | n2     # union (Total number of words in both Categories of connected Nodes)
        if(len(n1Un2)) > 0:
            similarity = round(len(n1In2)/len(n1Un2), 2)
        copurchaseGraphMusic.add_edge(asin, a.strip(), weight=similarity)


# Write copurchaseGraph data to file
fhw = open('amazon-music-copurchase.edgelist', 'wb')
networkx.write_weighted_edgelist(copurchaseGraphMusic, fhw)
fhw.close()
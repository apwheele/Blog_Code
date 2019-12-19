#Finding source incidents
library(igraph)

MyDir <- "C:\\Users\\axw161530\\Dropbox\\Documents\\BLOG\\SourceNearRepeats"
setwd(MyDir)

BMV <- read.csv(file="TheftFromMV.csv",header=TRUE)
summary(BMV)

#make a function
NearStrings <- function(data,id,x,y,time,DistThresh,TimeThresh){
	library(igraph) #need igraph to identify connected components
    MyData <- data
	SpatDist <- as.matrix(dist(MyData[,c(x,y)])) < DistThresh  #1's for if under distance
	TimeDist <-  as.matrix(dist(MyData[,time])) < TimeThresh #1's for if under time
	AdjMat <- SpatDist * TimeDist #checking for both under distance and under time
	diag(AdjMat) <- 0 #set the diagonal to zero
	row.names(AdjMat) <- MyData[,id] #these are used as labels in igraph
	colnames(AdjMat) <- MyData[,id] #ditto with row.names
	G <- graph_from_adjacency_matrix(AdjMat, mode="undirected") #mode should not matter
	CompInfo <- components(G) #assigning the connected components
	return(data.frame(CompId=CompInfo$membership,CompNum=CompInfo$csize[CompInfo$membership]))
}

#Quick example with the first ten records
BMVSub <- BMV[1:10,]
ExpStrings <- NearStrings(data=BMVSub,id='incidentnu',x='xcoordinat',y='ycoordinat',time='DateInt',DistThresh=30000,TimeThresh=3)
ExpStrings

#Second example alittle larger, with the first 5000 records
BMVSub2 <- BMV[1:5000,]
BigStrings <- NearStrings(data=BMVSub2,id='incidentnu',x='xcoordinat',y='ycoordinat',time='DateInt',DistThresh=1000,TimeThresh=3)

#Add them into the original dataset
BMVSub2$CompId <- BigStrings$CompId
BMVSub2$CompNum <- BigStrings$CompNum

#Number of chains
table(aggregate(CompNum ~ CompId, data=BigStrings, FUN=max)$CompNum)

#Look up the 9 incident
BMVSub2[BMVSub2$CompNum == 9,]

#Looking up a particular incident chains
BMVSub2[BMVSub2$CompId == 4321,]
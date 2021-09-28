// Source: https://www.geeksforgeeks.org/multi-source-shortest-path-in-unweighted-graph/
// C++ program to demonstrate
// multi-source BFS
#include <bits/stdc++.h>
using namespace std;
#define N 100000 + 1
#define inf 1000000

// This array stores the distances of the vertices
// from the nearest source
int dist[N];

// This Set contains the vertices not yet visited in
// increasing order of distance from the nearest source
// calculated till now
set<pair<int, int> > Q;

// Util function for Multi-Source BFS
void multiSourceBFSUtil(vector<int> graph[], int s)
{
	set<pair<int, int> >::iterator it;
	int i;
	for (i = 0; i < graph[s].size(); i++) {
		int v = graph[s][i];
		if (dist[s] + 1 < dist[v]) {

			// If a shorter path to a vertex is
			// found than the currently stored
			// distance replace it in the Q
			it = Q.find({ dist[v], v });
			Q.erase(it);
			dist[v] = dist[s] + 1;
			Q.insert({ dist[v], v });
		}
	}

	// Stop when the Q is empty -> All
	// vertices have been visited. And we only
	// visit a vertex when we are sure that a
	// shorter path to that vertex is not
	// possible
	if (Q.size() == 0)
		return;

	// Go to the first vertex in Q
	// and remove it from the Q
	it = Q.begin();
	int next = it->second;
	Q.erase(it);

	multiSourceBFSUtil(graph, next);
}

// This function calculates the distance of
// each vertex from nearest source
void multiSourceBFS(vector<int> graph[], int n,
						int sources[], int S)
{
	// a hash array where source[i] = 1
	// means vertex i is a source
	int source[n + 1];

	for (int i = 1; i <= n; i++)
		source[i] = 0;
	for (int i = 0; i <= S - 1; i++)
		source[sources[i]] = 1;

	for (int i = 1; i <= n; i++) {
		if (source[i]) {
			dist[i] = 0;
			Q.insert({ 0, i });
		}
		else {
			dist[i] = inf;
			Q.insert({ inf, i });
		}
	}

	set<pair<int, int> >::iterator itr;

	// Get the vertex with lowest distance,
	itr = Q.begin();

	// currently one of the sources with distance = 0
	int start = itr->second;

	multiSourceBFSUtil(graph, start);

	// Printing the distances
	for (int i = 1; i <= n; i++)
		cout << i << " " << dist[i] << endl;
}

void addEdge(vector<int> graph[], int u, int v)
{
	graph[u].push_back(v);
	graph[v].push_back(u);
}

// Driver Code
int main()
{
	// Number of vertices
	int n = 6;

	vector<int> graph[n + 1];

	// Edges
	addEdge(graph, 1, 2);
	addEdge(graph, 1, 6);
	addEdge(graph, 2, 6);
	addEdge(graph, 2, 3);
	addEdge(graph, 3, 6);
	addEdge(graph, 5, 4);
	addEdge(graph, 6, 5);
	addEdge(graph, 3, 4);
	addEdge(graph, 5, 3);

	// Sources
	int sources[] = { 1, 5 };

	int S = sizeof(sources) / sizeof(sources[0]);

	multiSourceBFS(graph, n, sources, S);

	return 0;
}

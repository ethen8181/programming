//============================================================================
// Name        : LeetCode.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <queue>
#include <vector>
#include <unordered_map>
#include <unordered_set>
using namespace std;


int findKthLargest(vector<int>& nums, int k) {
	sort(nums.begin(), nums.end());
	return nums[k - 1];
}

int partition(vector<int>& nums, int left, int right) {
    int pivot = nums[left];
    int l = left + 1, r = right;
    while (l <= r) {
        if (nums[l] < pivot && nums[r] > pivot)
            swap(nums[l++], nums[r--]);
        if (nums[l] >= pivot) l++;
        if (nums[r] <= pivot) r--;
    }
    swap(nums[left], nums[r]);
    return r;
}


vector<int> topKHeap(vector<int> &nums, int k) {
	// Leetcode 347
	unordered_map<int, int> counts;
	for (int num: nums) {
		counts[num]++;
	}

	// pair<int, int>: first is the frequency and second is the number
	priority_queue<pair<int, int>> pq;
	for (auto &count: counts) {
		pq.push(make_pair(count.second, count.first));
	}

	vector<int> vec;
	for (int i = 0; i < k; i++) {
		vec.push_back(pq.top().second);
		pq.pop();
	}
	return vec;
}


vector<int> topKBucket(vector<int> &nums, int k) {
	// Leetcode 347
	unordered_map<int, int> counts;
	for(int num: nums) {
		counts[num]++;
	}

	/*
	 * bucket sort
	 * use the count to indicate position of the bucket
	 * and the maximum possible count is total size of vector + 1
	 */
	vector<vector<int>> buckets(nums.size() + 1);
	for(auto &count: counts) {
		buckets[count.second].push_back(count.first);
	}

	vector<int> result;
	for (int i = buckets.size() - 1; i >= 0; i--) {
		for (int j = 0; j < buckets[i].size(); j++) {
			result.push_back(buckets[i][j]);
			if (result.size() == k) {
				return result;
			}
		}
	}
	return result;
}


class Solution207 {
public:
	bool canFinish(int numCourses, vector<pair<int, int>>& prerequisites) {
		vector<unordered_set<int>> graph = make_graph(numCourses, prerequisites);
		vector<int> indegree = compute_indegree(graph);

		// nodes with indegree of 0 are added to the pending set
		queue<int> pending;
		for (int i = 0; i < numCourses; i++) {
			if (!indegree[i]) {
				pending.push(i);
			}
		}

		int front, counter = 0;
		while (!pending.empty()) {
			front = pending.front();
			pending.pop();
			counter++;
			for (auto neighbor: graph[front]) {
				/*
				 * decrement dependency, and once
				 * its indegree hits 0, also add it to the
				 * pending set
				 */
				if (!(--indegree[neighbor])) {
					pending.push(neighbor);
				}
			}
		}
		return counter == numCourses;
	}

private:
	vector<unordered_set<int>> make_graph(int numCourses, vector<pair<int, int>>& prerequisites) {
		// convert the input pair to adjacent list format
		vector<unordered_set<int>> graph(numCourses);
		for (auto pre: prerequisites) {
			graph[pre.second].insert(pre.first);
		}
		return graph;
	}

	vector<int> compute_indegree(vector<unordered_set<int>>& graph) {
		vector<int> indegree(graph.size(), 0);
		for (auto neighbors: graph) {
			for (int neigh: neighbors) {
				indegree[neigh]++;
			}
		}
		return indegree;
	}
};


class Solution200 {
private:
	int m, n;

public:
	int numIslands(vector<vector<char>>& grid) {
		if (grid.empty()) {
			return 0;
		}

		int nIslands = 0;
		m = grid.size(), n = grid[0].size();
		vector<vector<bool>> visited(m, vector<bool>(n, false));
		for (int i = 0; i < m; i++) {
			for (int j = 0; j < n; j++) {
				if (grid[i][j] == '1' && !visited[i][j]) {
					markIslands(grid, visited, i, j);
					nIslands++;
				}
			}
		}
		return nIslands;
	}

private:
	void markIslands(vector<vector<char>>& grid, vector<vector<bool>>& visited, int i, int j) {
		if (i < 0 || j < 0 || i > m || j > n || visited[i][j] || grid[i][j] == '0') {
			return;
		}
		visited[i][j] = true;
		markIslands(grid, visited, i - 1, j);
		markIslands(grid, visited, i + 1, j);
		markIslands(grid, visited, i, j - 1);
		markIslands(grid, visited, i, j + 1);
	}
};


// Definition for singly-linked list.
struct ListNode {
	int val;
	ListNode *next;
	ListNode(int x): val(x), next(NULL) {}
};


class Solution206 {
	ListNode* reverse(ListNode* head) {
		ListNode* prev = NULL;
		while (head) {
			ListNode* temp = head->next;
			head->next = prev;
			prev = head;
			head = temp;
		}
		return prev;
	}
};


class Solution242_1 {
public:
	bool isAnagram(string s, string t) {
		if (s.length() != t.length()) {
			return false;
		}

		int n = s.length();
		unordered_map<char, int> counts;
		for (int i = 0; i < n; i++) {
			counts[s[i]]++;
			counts[t[i]]--;
		}
		for (auto &count: counts) {
			if (count.second) {
				return false;
			}
		}
		return true;
	}
};


class Solution242_2 {
public:
	bool isAnagram(string s, string t) {
		if (s.length() != t.length()) {
			return false;
		}

		int n = s.length();
		int counts[26] = {0};
		for (int i = 0; i < n; i++) {
			counts[t[i] - 'a']--;
		}
		for (int count: counts) {
			if (count) {
				return false;
			}
		}
		return true;
	}
};


struct TreeNode {
	int val;
	TreeNode* left;
	TreeNode* right;
	TreeNode(int val): val(val), left(NULL), right(NULL) {};
};


class Solution108 {
public:
	TreeNode* sortedArrayToBST(vector<int>& nums) {
		return helper(nums, 0, nums.size());
	}

	TreeNode* helper(vector<int>& nums, int start, int end) {
		if (start <= end) {
			return NULL;
		}
		int mid = (start + end) / 2;
		TreeNode* parent = new TreeNode(nums[mid]);
		parent->left = helper(nums, start, mid);
		parent->right = helper(nums, mid + 1, end);
		return parent;
	}
};


class Solution350 {
public:
	vector<int> intersect(vector<int>& nums1, vector<int>& nums2) {
		unordered_map<int, int> count;
		for (int num: nums2) {
			count[num]++;
		}

		vector<int> ans;
		for (int num: nums1) {
			if (count.find(num) != count.end() && count[num]-- > 0) {
				ans.push_back(num);
			}
		}
		return ans;
	}
};





int main() {
//	vector<int> nums = {3, 2, 1, 5, 6, 4};
//	//cout << findKthLargest(nums, 2) << endl;
//
//	int left = 0, right = nums.size() - 1;
//	cout << partition(nums, left, right) << endl;
//
//	vector<int>::iterator it;
//	for (it = nums.begin(); it != nums.end(); it++) {
//		cout << *it << flush;
//	}


	int k = 2;
	vector<int> nums = {1, 1, 1, 2, 2, 3};
	vector<int> vec1 = topKHeap(nums, k);
	vector<int> vec2 = topKBucket(nums, k);
	for (auto it = vec1.begin(); it != vec1.end(); it++) {
		cout << *it << endl;
	}


	return 0;
}

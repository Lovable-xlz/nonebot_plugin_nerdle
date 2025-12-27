# include<bits/stdc++.h>
using namespace std;
const int n = 20079, N = 5e5 + 5;
map<char, int> m;
bool vis[N];
vector<string> str[N];
int tot;
void init() {
	for(int i = 0; i <= 9; i++)
		m[i + '0'] = i;
	m['+'] = 10; m['-'] = 11; m['*'] = 12; m['/'] = 13; m['='] = 14;
}
int rev(int x) {
	return x ^ ((1 << 14) - 1);
}
void output(string x, string y) {
	tot++;
	printf("Possible choice #%d:\n", tot);
	for(int i = 1; i < x.size() - 2; i++)
		putchar(x[i]);
	puts("");
	for(int i = 1; i < y.size() - 2; i++)
		putchar(y[i]);
	puts("");puts("");
	return ;
}
int main() {
	freopen("dic-8.json", "r", stdin);
	freopen("equ.txt", "w", stdout);
	init();
	string s;
	cin >> s;
	for(int i = 1; i <= n; i++) {
		cin >> s;
		int tmp = 0;
		for(int i = 1; i < s.size() - 2; i++)
			tmp |= (1 << m[s[i]]);
		if(vis[rev(tmp)]) {
			for(auto st: str[rev(tmp)])
				output(st, s);
		}
		vis[tmp] = 1; str[tmp].push_back(s);
	}
	fclose(stdin);
	fclose(stdout);
	return 0;
}

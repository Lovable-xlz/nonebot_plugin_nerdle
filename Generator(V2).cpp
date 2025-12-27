# pragma GCC optimize(2)
# include<bits/stdc++.h>
using namespace std;
typedef long long ll;
const int len = 11;
const int INF = 0x7f7f7f7f;
const int oper[4] = {'+', '-', '*', '/'};
bool F;
char op[len << 2];
stack<ll> s;
stack<char> o;
int level(char ch) {
	if(ch == '+' || ch == '-') return 1;
	if(ch == '*' || ch == '/') return 2;
	return 0; 
}
bool check(ll m, ll n) {
	__int128 M = m, N = n;
	return M * N == (__int128)(m * n); 
}
bool calc() {
	ll x = s.top(); s.pop();
	ll y = s.top(); s.pop();
	char ch = o.top(); o.pop();
	if(ch == '+') {
		s.push(y + x);
		return 1;
	}
	else if(ch == '-') {
		s.push(y - x);
		return 1; 
	}
	else if(ch == '*') {
		if(!check(y, x)) return 0;
		s.push(y * x);
		return 1;
	}
	else if(ch == '/') {
		if(!x || y % x != 0) return 0; // 除数非 0 且能整除 
		s.push(y / x);
		return 1;
	}
	return 0;
}
int getlen(int res) {
	int x = (res <= 0); ll tmp = res; // 负数额外多一位 - 
	while(tmp != 0) x++, tmp /= 10;
	return x;
}
int precalc(int st, int pos, int md) { // md 为 1 时检查是否出现运算符 
	while(!s.empty()) s.pop();
	while(!o.empty()) o.pop();
	ll tmp = 0; bool flag = 0, ff = 0; // ff 记录是否有运算操作，没有的话直接返回 INF 
	for(int i = st; i <= pos; i++) {
		if(isdigit(op[i]))
			tmp = tmp * 10 + op[i] - '0', flag = 1;
		else {
			if(!flag) continue;
			if(!tmp) return INF;
			ff = 1;
			s.push(tmp), tmp = 0;
			while(!o.empty() && level(op[i]) <= level(o.top()))
				if(!calc()) return INF;
			o.push(op[i]);
		}
	}
	if(flag) s.push(tmp);
	while(!o.empty())
		if(!calc()) return INF;
	if(!ff && md) return INF;
	return s.top();
}
void dfs(int now, int md) { // md 为 1 说明当前数已经被敲定，跳过枚举数字环节 
	if(now > len - 1) return ; // = 最少在倒数第二个
	if(now > 1 && isdigit(op[now - 1])) { // 最后一位必须是数 
		ll res = precalc(1, now - 1, 1);
		if(res != INF) {
			int l = getlen(res);
			if(now + l == len) {
				if(F) printf(",");
				F = 1;
				printf("\n\t\"");
				for(int i = 1; i < now; i++)
					putchar(op[i]);
				printf("=%lld", res);
				printf("\"");
			}
		}
	}
	if(!md) {
		for(int i = 0; i <= 9; i++) {
			if(i == 0 && (now == 1 || (now > 1 && !isdigit(op[now - 1]))))
				continue; // 参与运算的值非 0 
			op[now] = '0' + i;
			dfs(now + 1, 0);
		}
	}
	if(now > 1 && isdigit(op[now - 1])) { // 前一位是数字就可以放运算符
		for(int i = 0; i < 4; i++) {
			op[now] = oper[i];
			if(i == 3) { // 除法直接把除数一同敲定
				int tmp = 0; ll res = 0;
				for(int j = now - 1; j >= 1; j--) { // 找到前面首个 + 或 - 
					if(op[j] == '+' || op[j] == '-') break;
					tmp = j;
				}
				res = precalc(tmp, now - 1, 0);
				ll maxj = 1; tmp = len - now - 2;
				for(int i = 1; i <= tmp; i++) maxj *= 10; 
				maxj = min(maxj - 1, (ll)sqrt(res));
				for(int j = 1; j <= maxj; j++)
					if(res % j == 0) {
						int le = getlen(j); tmp = j;
						for(int k = now + le; k >= now + 1; k--)
							op[k] = '0' + tmp % 10, tmp /= 10;
						dfs(now + le + 1, 1);
						if(now + le + 1 > len - 1) break; // 位数超了直接跳 
						if(j * j != res) {
							le = getlen(res / j); tmp = res / j;
							for(int k = now + le; k >= now + 1; k--)
								op[k] = '0' + tmp % 10, tmp /= 10;
							dfs(now + le + 1, 1);
						}
					}
			}
			else dfs(now + 1, 0);
		}
	}
	return ;
}
void init() {
	printf("[");
	return ;
}
void tini() {
	printf("\n]\n");
	return ;
}
signed main() {
	freopen("dic-11-2.json", "w", stdout);
	init();
	dfs(1, 0); 
	tini();
	fclose(stdout);
	return 0; 
}

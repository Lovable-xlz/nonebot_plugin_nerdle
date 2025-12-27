# pragma GCC optimize(2)
# include<bits/stdc++.h>
using namespace std;
const int len = 11;
const int INF = 0x7f7f7f7f;
const int oper[4] = {'+', '-', '*', '/'};
int ans;
bool F;
char op[len + 5];
stack<int> s;
stack<char> o;
int level(char ch) {
	if(ch == '+' || ch == '-') return 1;
	if(ch == '*' || ch == '/') return 2;
	return 0; 
}
bool calc() {
	int x = s.top(); s.pop();
	int y = s.top(); s.pop();
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
	int x = (res <= 0), tmp = res; // 负数额外多一位 - 
	while(tmp != 0) x++, tmp /= 10;
	return x;
}
int precalc(int pos) {
	while(!s.empty()) s.pop();
	while(!o.empty()) o.pop();
	int tmp = 0; bool flag = 0, ff = 0; // ff 记录是否有运算操作，没有的话直接返回 INF 
	for(int i = 1; i <= pos; i++) {
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
	if(!ff) return INF;
	return s.top();
}
void dfs(int now) {  
	if(now > len - 1) return ; // = 最少在倒数第二个
	if(now > 1 && isdigit(op[now - 1])) { // 最后一位必须是数 
		int res = precalc(now - 1);
		if(res != INF) {
			int l = getlen(res);
			if(now + l == len) {
				ans++;
				if(F) printf(",");
				F = 1;
				printf("\n\t\"");
				for(int i = 1; i < now; i++)
					putchar(op[i]);
				printf("=%d", res);
				printf("\"");
			}
		}
	}
	for(int i = 0; i <= 9; i++) {
		if(i == 0 && (now == 1 || (now > 1 && !isdigit(op[now - 1]))))
			continue; // 参与运算的值非 0 
		op[now] = '0' + i;
		dfs(now + 1);
	}
	if(now > 1 && isdigit(op[now - 1])) { // 前一位是数字就可以放运算符
		for(int i = 0; i < 4; i++) {
			op[now] = oper[i];
			dfs(now + 1); 
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
int main() {
	freopen("dic-11.json", "w", stdout);
	init();
	dfs(1); 
	tini();
	fclose(stdout);
	return 0; 
}

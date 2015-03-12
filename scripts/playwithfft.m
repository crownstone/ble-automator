%t=0:0.001:2;
%t=t/5;
%x=2*sin(20*pi*t) + sin(100*pi*t);

%b=[1   5   1   5   1   5   1   7   1   7   1   6];
b=[13   54   14   57   12   59   17   73   16   74   14   65];
b=[16   57   15   59   15   59   15   66   15   67   15];

c=b<30;
b=b*100;
c=c*30;

len=b;
val=c;
i = cumsum(len);             % LENGTH(LEN) flops
j = zeros(1, i(end));
j(i(1:end-1)+1) = 1;         % LENGTH(LEN) flops
j(1) = 1;
x = val(cumsum(j));          % SUM(LEN) flops

t=1:length(x);


% create blockwave from this


%split_x=max(x)/2;
%split_x=0;
%x(x<split_x)=0;
%x(x>split_x)=1;

trans=find(diff(x>0));

subplot(2,1,1);
plot(1000*t,x);
grid;
xlabel("Time in milliseconds");
ylabel("Signal amplitude");

subplot(2,1,2);
y=fft(x);

y=abs(y)/1000;

smp_len=100;
t=t(1:smp_len);
y=y(1:smp_len);

plot(t, y);
xlabel("Frequency");
ylabel("Signal amplitude");

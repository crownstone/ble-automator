device='fridge';
%device='bulb';
file=['../data/' device '.txt.filtered'];
c=load('-ascii',file);
ofile=[device '.png'];

% get time stamps and make them a bit smaller
d=c(:,1)-c(1,1);
%d=c(:,1);

% get values
e=c(:,2:end);

% we want to pair d(1,1) with e(1,:)
% the difference between d(n,1) and d(n+1,1) is something around 20 seconds
% the values are more on the level of 0.1 seconds apart
% so, we want to introduce d(n,1)+0.1, d(n+1)+0.1*2, etc. for the number of values

samples=size(e,1); 
val_len=size(e,2); % 129

sec=0.1; % seconds apart per value
tmp=cumsum(ones(1,val_len)*(sec));
r=repmat(tmp,samples,1);

rd=repmat(d,1,val_len);

rrd=r+rd;
% size rrd should be equal to size e

x=rrd'(:);
y=e'(:);

filter_start=1;
filter_end=length(x);
%filter_start=2000;
%filter_end=3000;
x=x(filter_start:filter_end);
y=y(filter_start:filter_end);

% data error, remove stuff above threshold
threshold=100;
y(y>threshold)=0;

% show log
y=log(y+1);

% subsample
sample_freq=100;
x=x(1:sample_freq:end);
y=y(1:sample_freq:end);

figure(1);
clf();
plot(x,y);

% try to save to file
saveas(1,ofile);

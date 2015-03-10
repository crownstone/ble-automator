device='fridge';
device='bulb';
device='bulb1';
file=['../data/' device '.txt.filtered'];
c=load('-ascii',file);
ofile=[device '.png'];

% get time stamps and make them a bit smaller
d=c(:,1)-c(1,1);
%d=c(:,1);

% clock times are in reverse order
tbeg=c(:,end);
tend=c(:,2);
tdff=tend-tbeg;
% assume clock to take same time all the time
tdiff=tdff(1);

% get values
data_start=3;
data_end=1;
%e=c(:,2:end); if there are no clock times involved
e=c(:,data_start:end-data_end);

% prepend every series of value with 0, as well as append it, so if they are far apart it won't generate
% weird lines
z=zeros(size(e,1),1);
e=[z e z];

% cumulative vector (current average, but without scaling)
c1=sum(c(:,data_start:end-data_end)')'/length(e);

% we want to pair d(1,1) with e(1,:)
% the difference between d(n,1) and d(n+1,1) is something around 20 seconds
% the values are more on the level of 0.1 seconds apart
% so, we want to introduce d(n,1)+0.1, d(n+1)+0.1*2, etc. for the number of values

samples=size(e,1); 
val_len=size(e,2); % 129 without the two fake zeros on both sides

printf("There are %i samples of size %i each\n", samples, val_len);

sec=0.02; % seconds apart per value
sec=tdiff/(1000*val_len);
printf("Plot values %f seconds apart\n", sec);
% create for each timestamp an additiona val_len values sec apart
tmp=cumsum(ones(1,val_len)*(sec));
% do this for every sample
r=repmat(tmp,samples,1);
% copy each timestamp to all val_len columns
rd=repmat(d,1,val_len);

rrd=r+rd;
% size rrd should be equal to size e

x=rrd'(:);
y=e'(:);

printf("By appending all data points from all samples we got a vector of size %i\n", length(y));

filter_start=1;
filter_end=length(x);
%filter_start=2000;
%filter_end=3000;
x=x(filter_start:filter_end);
y=y(filter_start:filter_end);

% data error, remove stuff above threshold
%threshold=100;
%y(y>threshold)=0;

% show log
%y=log(y+1);

% subsample
%sample_freq=100;
%x=x(1:sample_freq:end);
%y=y(1:sample_freq:end);

%figure(1);
subplot(1,2,1);
%clf();
plot(x,y);

%axis ("square");
subplot(1,2,2);

plot(d,c1,'.');
p=ylim
set(gca, "ylim", [0 p(2) * 1.1]);
%axis ("square");

% try to save to file
%saveas(1,ofile);

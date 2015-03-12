
devices={"fridge", "bulb"};
devices={"fridge"};

% loop over everything multiple times
for iter = 1:length(devices)

device=devices{iter};

file=['../data/' device '.txt.filtered'];
c=load('-ascii',file);
ofile=[device '.png'];

% configuration options
smooth_raw_flag=false;
smooth_avg_flag=false;
remove_above_threshold_flag=true;
make_log_flag=false;
subsample_flag=false;
apply_fft_flag=true;
limit_sample_count_flag=true;
make_block_flag=true;
interpolate_flag=true;

if (limit_sample_count_flag)
	limit=500;
	c=c(1:limit,:);
end

% get time stamps and make them a bit smaller (by subtracting first time stamp)
d=c(:,1)-c(1,1);

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

% data error, remove stuff above threshold
if (remove_above_threshold_flag)
	threshold=80;
	e(e>threshold)=0;
end

% cumulative vector (current average, but without scaling)
c1=sum(e')'/length(e);

% prepend every series of value with 0, as well as append it, so if they are far apart it won't generate
% weird lines
z=zeros(size(e,1),1);
e=[z e z];

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

% time
x=rrd'(:);

% data
y=e'(:);

printf("By appending all data points from all samples we got a vector of size %i\n", length(y));

filter_start=1;
filter_end=length(x);
%filter_start=2000;
%filter_end=3000;
x=x(filter_start:filter_end);
y=y(filter_start:filter_end);

if (smooth_raw_flag)
	wndw=1000;
	printf("Smooth raw data with window size %i\n", wndw);
	y = imfilter(y, fspecial('average', [wndw 1]));
end

if (smooth_avg_flag)
	wndw=10;
	printf("Smooth averaged data with window size %i\n", wndw);
	c1 = imfilter(c1, fspecial('average', [wndw 1]));
end

% the data points are not uniformly spaced over the time
if (interpolate_flag) 
	max_d=max(d);
	min_d=min(d);
	min_d=0;
	len_d=length(d);
	trans=find(diff(y>max(y)/2));
%	len_d=100;
	d1=min_d:(max_d-min_d)/(len_d-1):max_d;
	d1=d1';
	st=1;
	len=450;
	d1=d1(st:st+len);
	d=d(st:st+len);
	c1=c1(st:st+len);
	y1=griddatan(d,c1,d1,"nearest");
	d=d1;
	c1=y1;
end


% show log
if (make_log_flag) 
	y=log(y+1);
end

% subsample
if (subsample_flag)
	sample_freq=100;
	x=x(1:sample_freq:end);
	y=y(1:sample_freq:end);
end

if (make_block_flag) 
	% for raw data
	block_threshold=max(y)/2;
	y(y<block_threshold)=0;
	y(y>=block_threshold)=block_threshold*2;

	% for averaged data
	block_threshold=max(c1)/2;
	c1(c1<block_threshold)=0;
	c1(c1>=block_threshold)=block_threshold*2;

	trans=find(diff(c1>block_threshold));
	fl=diff(trans);
	printf("The following is a problem. The square wave is not really regular. It has phase shifts.\n");
	printf("Note that this is for the averaged data!\n");
	block_wave_transitions=fl'
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Graphics
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
figure(iter);
clf();
subplot(2,2,1);
plot(x,y);

% adjust limits
p=ylim;
marg=p(2)*0.1;
low=0-marg; 
high=p(2)+marg;
set(gca, "ylim", [low high]);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subplot(2,2,2);

%plot(d,c1,'.');
plot(d,c1);
p=ylim;
marg=p(2)*0.1;
low=0-marg; 
high=p(2)+marg;
set(gca, "ylim", [low high]);
%axis ("square");

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subplot(2,2,3);
periodogram(c1);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subplot(2,2,4);
if (apply_fft_flag) 
	fc1=fft(y/10000);
	flen=length(fc1)/1000;
	fakey=1:flen;
	fc1=fc1(fakey);
	plot(fakey,abs(fc1));
end


% try to save to file
%saveas(1,ofile);

end




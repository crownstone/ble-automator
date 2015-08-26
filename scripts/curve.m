% Load data
%device='bulb'
%device='fridge'
device='tv'
%device='halogen'

flag_timestamped=false
flag_hold_on=false
flag_reverse_time=false

file=['../data/' device '.txt.filtered2']
data=load('-ascii', file);
datetimes  = data(:,1) - data(1,1);
if (flag_timestamped)
	indsplit = (size(data,2)-1)/2+1;
	current = data(:,2:indsplit);
	timestamps = (data(:,indsplit+1:end) - data(:,indsplit+1)) / 32768;
else
	current = data(:,3:end-1);
	if (flag_reverse_time)
		timestamps = linspace(0, data(:,2)-data(:,end), size(data,2)-3);
	else
		timestamps = linspace(0, data(:,end)-data(:,2), size(data,2)-3);
	end
end


% Find curves where the device is on
[i,j]=find((max(current,[],2)>10 & max(current,[],2)<500));
%[i,j]=find(max(current,[],2)>10);
indf=i;
maxcurrent=max(max(current(indf,:)));
maxtime=max(max(timestamps(indf,:)));

% Plot all curves
figure(1);
hold off;
for i=1:size(indf)
	plot(timestamps(indf(i),:), current(indf(i),:), '-x')
	if (flag_hold_on)
		hold on
	else
		axis([0 maxtime 0 maxcurrent])
		drawnow
		%if (max(vf(indf(i),:)) > 20)
		sleep(1)
		%else
		%	sleep(0.1)
		%end
	end
end

file=[device '-curve.png']
%print(1, file)

waitforbuttonpress;

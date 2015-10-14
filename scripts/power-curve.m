% Load data
%device='bulb'
%device='fridge'
device='power'
%device='halogen'

flag_hold_on=false

file=['../data/' device '.txt.filtered']
data=load('-ascii', file);
index=1;

datetimes = data(:,index) - data(1,index);
index+=1

numSamples = data(1,2);
index+=1

numCurrentSamples = ceil(numSamples/2);
numVoltageSamples = floor(numSamples/2);

current = data(:,index:index-1+numCurrentSamples);
index+=numCurrentSamples

voltage = data(:,index:index-1+numVoltageSamples);
index+=numVoltageSamples

timestamps = (data(:,index:index-1+numSamples) - data(:,index)) / 32768;
index+=numSamples

% Find curves where the device is on
%[indf,j]=find((max(current,[],2)>10 & max(current,[],2)<500));
%[indf,j]=find(max(current,[],2)>10);
indf=1:size(current,1)

mincurrent=min(min(current(indf,:)));
maxcurrent=max(max(current(indf,:)));
minvoltage=min(min(voltage(indf,:)));
maxvoltage=max(max(voltage(indf,:)));
maxtime=max(max(timestamps(indf,:)));

% Plot all curves
figure(1);
hold off;
figure(2);
hold off;
for i=1:length(indf)
	figure(1)
	plot(timestamps(indf(i),1:2:end), current(indf(i),:), '-x')
	if (flag_hold_on)
		hold on
	else
		axis([0 maxtime mincurrent maxcurrent])
		drawnow
%		sleep(1)
	end
	figure(2)
	plot(timestamps(indf(i),2:2:end), voltage(indf(i),:), '-x')
	if (flag_hold_on)
		hold on
	else
		axis([0 maxtime minvoltage maxvoltage])
		drawnow
		sleep(1)
	end
end

waitforbuttonpress;


% Load data
device='fridge'

flag_hold_on=true

file=['../data/' device '.txt.filtered']
df=load('-ascii', file);
tf=df(:,1) - df(1,1);
vf=df(:,2:end);

% Find curves where the device is on
[i,j]=find((max(vf,[],2)>1 & max(vf,[],2)<500));
%[i,j]=find(max(vf,[],2)>1);
indf=i;
maxf=max(max(vf(i,:)));

% Plot all curves
figure(1);
hold off;
for i=1:size(indf)
	plot(vf(indf(i),:))
	if (flag_hold_on)
		hold on
	else
		axis([0 size(vf,2) 0 maxf])
		drawnow
		if (max(vf(indf(i),:)) > 20)
			sleep(1)
		else
			sleep(0.1)
		end
	end
end
file=[device '-curve.png']
print(1, file)

waitforbuttonpress;

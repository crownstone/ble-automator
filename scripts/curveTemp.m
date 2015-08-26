% Load data
address='C5:18:C4:52:40:35'

file=['../data/temp_' address '.txt.filtered']
data=load('-ascii', file);

% shift timestamp with first timestamp
timestamps = data(:,1) - data(1,1);

% data itself
values = data(:,2);

% Plot all curves
figure(1);
hold off;
for i=1:1
	plot(timestamps, values, '-x')
end

file=['temp' address '-curve.png']
print(1, file)

waitforbuttonpress;


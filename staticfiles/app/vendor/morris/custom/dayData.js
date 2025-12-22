// Morris Days
var day_data = [
	{"period": "2016-10-01", "licensed": 3213, "Goldfinch": 887},
	{"period": "2016-09-30", "licensed": 3321, "Goldfinch": 776},
	{"period": "2016-09-29", "licensed": 3671, "Goldfinch": 884},
	{"period": "2016-09-20", "licensed": 3176, "Goldfinch": 448},
	{"period": "2016-09-19", "licensed": 3376, "Goldfinch": 565},
	{"period": "2016-09-18", "licensed": 3976, "Goldfinch": 627},
	{"period": "2016-09-17", "licensed": 2239, "Goldfinch": 660},
	{"period": "2016-09-16", "licensed": 3871, "Goldfinch": 676},
	{"period": "2016-09-15", "licensed": 3659, "Goldfinch": 656},
	{"period": "2016-09-10", "licensed": 3380, "Goldfinch": 663}
];
Morris.Line({
	element: 'dayData',
	data: day_data,
	xkey: 'period',
	ykeys: ['licensed', 'Goldfinch'],
	labels: ['Licensed', 'Goldfinch'],
	resize: true,
	hideHover: "auto",
	gridLineColor: "#e1e5f1",
	pointFillColors:['#ffffff'],
	pointStrokeColors: ['#af772b'],
	lineColors:['#af772b', '#da9d46', '#e0ac69', '#f1c17d', '#ffdbac'],
});
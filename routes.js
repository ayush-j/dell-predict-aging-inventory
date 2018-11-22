var express = require('express');
var app = module.exports = express();

var ml = require("./ml-connect");

var db = require('./db-connect');

app.get('/', function(req, res, next) {
	res.render('index', { title: 'Predicting Aging Inventory' });
});


app.get('/dashboard', function(req, resx, next) {
	db.query('SELECT * FROM inventory I INNER JOIN 3pl_info PL ON PL.3PLID=I.3PLID LIMIT 500', function (err, rows, fields) {
		if (err) throw err;
		var mldata = rows.map(function(x){ return x.PRICE; });
		console.log(mldata);
		var postdata = JSON.stringify(mldata);
		ml.invoke("predict", postdata, function(error, res, more) {
		    console.log(res);
		    console.log(rows.length);
		    if(!res) res='';
			resx.render('dashboard', { title: 'Predicting Aging Inventory', rows: rows, mlr: res.split('|')});
		});

	})
});


app.get('/about', function(req, res, next){
	res.render('about', { title: 'Predicting Aging Inventory' })
});

app.get('/product/view/:id', function(req, res, next){
	db.query(`SELECT * FROM product_list WHERE PRODUCT_ID=${req.params.id}`, function(err, rows, field){
		var item = rows[0];
		db.query('SELECT * FROM prod_spec_info WHERE Type="' + item.TYPE + '"', function(err, rows, field){
			res.render('proddetails', {title: 'Predicting Aging Inventory', item: item, specsInfo: rows[0]});
		});

	});
});

app.get('/inventory/view/:id', function(req, res2, next){
	db.query(`SELECT * FROM inventory I INNER JOIN 3pl_info PL ON PL.3PLID=I.3PLID INNER JOIN product_list L ON L.PRODUCT_ID=I.PRODUCT_ID WHERE I.ID=${req.params.id}`, function(err, rows, field){
		var item = rows[0];
		db.query('SELECT * FROM prod_spec_info WHERE Type="' + item.TYPE + '"', function(err, specinfo, field){

			db.query('SELECT * FROM 3pl_info', function(err, rows, field){

				var postdata = JSON.stringify([item.PRICE]);
				ml.invoke("predict", postdata, function(error, res, more) {
				    if(!res) res='';console.log(postdata, res);

					res2.render('invdetails', {title: 'Predicting Aging Inventory', item: item, specsInfo: specinfo[0]||{}, pllist: rows, mlres: res.split('|')[0]});
				});
			});
		});

	});
});


app.get('/inventory', function(req, res, next){

	db.query('SELECT L.*, COUNT(L.PRODUCT_ID) AS AVAILABLE FROM product_list L INNER JOIN inventory I ON L.PRODUCT_ID=I.PRODUCT_ID GROUP BY L.PRODUCT_ID', function (err, rows, fields) {
		if (err) throw err;

		res.render('inventory', { title: 'Predicting Aging Inventory', rows: rows });

	})


});


app.get('/mlstats', function(req, res, next){


		res.render('mlstats', { title: 'Predicting Aging Inventory' });


});

app.get('/runaction', function(req, res, next){
	console.log(req.body, req.query);
	if(req.query.action == 'move3pl'){

	}
	res.json({'test': 1});
});
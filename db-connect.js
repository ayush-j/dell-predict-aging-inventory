var mysql = require('mysql');


module.exports = mysql.createConnection({
	host     : 'localhost',
	user     : 'root',
	password : 'rootgroot',
	database : 'dell_aging_inv'
});

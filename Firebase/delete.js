var admin = require("firebase-admin");
var fs = require('fs');
var path = require('path');
var string = fs.readFileSync(path.resolve(__dirname, "coursica-2-firebase-adminsdk-t9nom-9273af3963.json"), 'utf8');
var serviceAccount = JSON.parse(string);

var deletePath = process.argv[2];

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://coursica-2.firebaseio.com"
});

var ref = admin.database().ref(deletePath);
ref.remove(function(error) {
  if (error) console.error(error)
  process.exit()
})
var admin = require("firebase-admin");
var fs = require('fs');
var path = require('path');
var string = fs.readFileSync(path.resolve(__dirname, "coursica-2-firebase-adminsdk-t9nom-9273af3963.json"), 'utf8');
var serviceAccount = JSON.parse(string);

var dataFile = process.argv[2];
var writeLoc = process.argv[3];
var version = process.argv[4];

var doneUploading = false;
var uploadChunk = function(ref, refUrl, i, chunks) {
total = chunks.length;
if (i < total) {
	ref.update(chunks[i], function(error) {
	    if (error) {
	      console.log(refUrl + " data could not be updated for chunk " + (i+1) + ": " + error);
	    } else {
	      console.log(refUrl + " data updated successfully for chunk " + (i+1) + " of " + total);
	    }
	    uploadChunk(ref, refUrl, i + 1, chunks);
	  });
} else {
	process.exit();
}
};

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://coursica-2.firebaseio.com"
});

var string = fs.readFileSync(path.resolve(__dirname, '../' + dataFile), 'utf8');
data = JSON.parse(string);

function sizeString(size) {
  return '(~' + (3 * size / (1024*1024)).toFixed(1) + ' MB)'
}

var CHUNK_SIZE = 4*1024*1024; // 4 million chars or ~12 MB per chunk
var chunks = [];
var chunk = {}; 
var size = 0;

var totalSize = 0;
for (var key in data) {
  totalSize += JSON.stringify(data[key]).length
}
console.log(refUrl, 'Total data size', sizeString(totalSize))

function addChunk() {
  console.log('Created chunk of size', sizeString(size))
  chunks.push(chunk);
  chunk = {};
  size = 0;
}

for (var key in data) {
  size += JSON.stringify(data[key]).length;
  chunk[key] = data[key];
  if (size > CHUNK_SIZE) {
    addChunk()
  }
}
addChunk()

var refUrl = "/v" + version + "/" + writeLoc;
var ref = admin.database().ref(refUrl);
console.log('Going to upload ', chunks.length, 'chunks', 'to:', refUrl);
uploadChunk(ref, refUrl, 0, chunks);
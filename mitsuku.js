var m = require('mitsuku-api')();
 
 m.send(process.argv.slice(2).join(" "))
   .then(function(response){
       console.log(response);
         });

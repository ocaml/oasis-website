ci = require("ci")

ci.init()

ci.exec("make", "all")
ci.exec("make", "deploy")

ci = require("ci")

ci.init()

ci.exec("make", "distclean")
ci.exec("make", "all")
ci.exec("fab", "deploy", "--user=gildor-jenkins")

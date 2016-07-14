
# http://rmflight.github.io/posts/2014/07/analyses_as_packages.html

# "devtools", "roxygen2", "rsconnect", "testthat", "DT"
library(devtools)
library(roxygen2)
setwd('/Users/ethen/Desktop')

package_name <- 'cat'

# create the package
create(package_name)

# change the directory to the package
# and document the function
setwd(package_name)
document()

?install

# http://r-pkgs.had.co.nz/package.html

# mimicks what happens when the package is installed and loaded
load_all()

?cat_function
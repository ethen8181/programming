name := "MyProject"

version := "0.1"

scalaVersion := "2.12.4"

// there's no need to tell SBT where to look for the file,
// however, when a library is not in a standard repo, we can
// tell SBT where to look for it by adding a resolver
// the pattern is:
// resolvers += "repository name" at "location"
// e.g.
// resolvers += "Typesafe" at "http://repo.typesafe.com/typesafe/releases/"

// a managed dependency is a dependency that's managed by
// our build tool, in this case .sbt. The jar file and its
// dependencies will be downloaded and included automatically.
// Under the covers, SBT uses Apache Ivy as its dependency manager
// meaning we must specify the groupID % artifactID % revision % configuration
libraryDependencies ++= Seq(
    // the %% adds the Scala version to the artifactID, this is a
    // common practice as modules may be compiled for different
    // Scala versions, thus scalatest will automatically become
    // scalatest_[scala version];
    // in some dependencies, the % test is added after the revision;
    // this means the dependency we're defining will only be added
    // to the classpath for the Test configuration, thus this is useful
    // for adding dependencies that will be used when we wish to test
    // our application, but not when we wish to compile and run the application
    "org.scalactic" %% "scalactic" % "3.0.+",
    "org.scalatest" %% "scalatest" % "3.0.+" % "test")


// if we only have one main method in our project then we don't need
// to specify the following configuration

// set the main class for packaging the main jar
mainClass in (Compile, packageBin) := Some("foo.Main")

// set the main class for the main 'sbt run' task
mainClass in (Compile, run) := Some("foo.Main")

// for publishLocal
publishTo := Some(Resolver.file("file", new File("/Users/ethen/tmp")))
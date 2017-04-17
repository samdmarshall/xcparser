# xcparse

xcparse is a python library for parsing and working with Xcode workspace and project files.

## Support

xcparse supports all modern objects found in xcodeproj files, and many legacy object. The parsing component of this library is complete and production ready. There are additional features that I am adding to make complex operations, such as resolving dependency build ordering, easy to perform.


## Examples

Loading a project or workspace

	from xcparse import xcparse
	
	root = xcparse(path_to_xcodeproj_or_xcworkspace);


Get a list of projects

	root = xcparse(path_to_xcodeproj_or_xcworkspace);
	
	project_list = root.projects();


Get a list of schemes

	root = xcparse(path_to_xcodeproj_or_xcworkspace);
	
	scheme_list = root.schemes();

Please explore the API for what it can offer you.

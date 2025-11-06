Given the telescope is in ON state
When I invoke AssignResources on CN with arraylayout 
Then SN arraylayout attribute gets updated
And DLN target data attribute gets updated with arraylayout provided by subarray


without AssignResources arraylayout json it will take default
# Json for AssignResources needs to be updated
assing -> configure 
### test_field_resolution_multiple_inheritance_with_child_field_defined

Test for field resolution in case of multiple inheritance with the same field defined in ChildWithMultipleParentsAndTheSameField.

**Test Scenario**

- Create an instance of ChildWithMultipleParentsAndTheSameField
- Check the name field default value

### test_field_resolution_multiple_inheritance_without_child_field_defined

Test for field resolution in case of multiple inheritance without the same field in ChildWithMultipleParents and ChildWithMultipleParentsWithDifferntOrder.

**Test Scenario**

- Create instances of ParentBM and ChildWithMultipleParents
- Check the name field default value

### test_field_resolution_single_inheritance

Test for field resolution in case of single inheritance without defining the same field in Child.

**Test Scenario**

- Create instances of ParentA, ParentB and Child.
- Check and compare the name field default value.

### test_field_resolution_single_inheritance_with_child_field_defined

Test for field resolution in case of single inheritance with the same field defined in ChildWithTheSameField.

**Test Scenario**

- Create an instance of ChildWithTheSameField
- Check the name field default value

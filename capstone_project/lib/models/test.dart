import 'package:json_annotation/json_annotation.dart';
import 'package:capstone_project/models/reactive.dart';

/// This allows the `User` class to access private members in
/// the generated file. The value for this is *.g.dart, where
/// the star denotes the source file name.
part 'test.g.dart';

/// An annotation for the code generator to know that this class needs the
/// JSON serialization logic to be generated.
@JsonSerializable()
class Test {
  Test(
    this.tID,
    this.tName,
    this.tDate,
    this.tNotes,
    this.baseline,
    this.iID,
    // this.dynamicTest,
    // this.staticTest,
    this.reactive,
  );

  @JsonKey(required: true)
  int tID;

  @JsonKey(required: true)
  String tName;

  @JsonKey(required: true)
  String tDate;

  @JsonKey(required: true)
  int iID;

  String? tNotes;
  int? baseline;
  // DynamicTest? dynamicTest;
  // StaticTest? staticTest;
  Reactive? reactive;

  // List<Test> tests;

  /// A necessary factory constructor for creating a new Incident instance
  /// from a map. Pass the map to the generated `_$IncidentFromJson()` constructor.
  /// The constructor is named after the source class, in this case, Incident.
  factory Test.fromJson(Map<String, dynamic> json) => _$TestFromJson(json);

  /// `toJson` is the convention for a class to declare support for serialization
  /// to JSON. The implementation simply calls the private, generated
  /// helper method `_$UserToJson`.
  Map<String, dynamic> toJson() => _$TestToJson(this);
}
class Student{
  constructor(){
    this.id=1;
    this.enrolled = false;
  }
  isActive(){
    console.log("check");
    return this.enrolled;
  }
}

s = new Student();

s.isActive();
// Check

console.log(typeof(Student));
// function

console.log(typeof(s));
// object

console.log(s.isActive());
// false
console.log(Student.prototype.isActive());
// undefined

console.log(s.isActive);
// function
console.log(Student.isActive);
// undefined 

Student.prototype.isActive = function(){
  console.log("Updated isActive in Student");
  return this.enrolled;
}

s.isActive();
// Updated isActive in Student;

console.log(s.toString())
// [object Object]

Student.prototype.toString = function(){
  return this.id.toString();
}

console.log(s.toString());
// 1

console.log(Object.toString());
console.log(Function.toString())
// function Object() {[native code]}
// Since this is just a prototype

console.log(Object.prototype.toString());
console.log((new Object()).toString());
console.log({}.toString());
// All the object instances, when run toString, just return [object Object]

console.log((new Function).toString());
// converts an instance of function(), and since it is blank, returns function anonymous. 

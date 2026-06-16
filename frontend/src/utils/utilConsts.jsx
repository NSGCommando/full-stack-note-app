/**
 * A mapping dictionary for replacing specific column names for UI improvements.
 * Helps bypass the need for multiple edge-cases with UI render for table columns inside the component itself.
 */
export const columnLabels = {
  is_admin: "Role",
  id: "S.No."
};

/**
 * A mapping dictionary for injecting specific values if specific values are detected.
 * Helps bypass the need for multiple edge-cases with UI render for column values.
 * It can substitute a function for a value too, which is how the is_admin replacer works.
 */
export const columnFormatter = {
  is_admin:(value)=>value? "Admin":"User",
  id:(_,index)=> index+1
};

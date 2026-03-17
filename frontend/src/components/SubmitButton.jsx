import "../styles/Components.css"

function SubmitButton({id, children, disabled }) {
  return (
    <button 
    id={id}
    type="submit" 
    className="submit-button" 
    disabled={disabled}>
      {children}
    </button>
  );
}

export default SubmitButton;
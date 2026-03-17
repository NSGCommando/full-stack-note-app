import "../styles/Components.css"

function TextInput({label, id, ...inputParams}) //Take label separately and collect all other params into a rest parameter
{
    return(
        <div className="text-input-group">
            <label htmlFor={id}>{label}</label>
            {/*destructure the rest parameter to get all parameters (type, value, onChange) */}
            <input id={id} className="text-input" {...inputParams}/>
        </div>
    );
}

export default TextInput
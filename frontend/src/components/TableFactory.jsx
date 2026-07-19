import { titleCaseFormat } from "../utils/utilFuncs";
import { columnLabels, columnFormatter } from "../utils/utilConsts";
import "../styles/Components.css"
function TableFactory({dataList, id, ...props}){
    let headers =[]
    if(!dataList || dataList.length===0){return (<p>No data found</p>);}
    if (props.deleteEntry){headers = [...Object.keys(dataList[0]),"Actions"]}
    else{headers = [...Object.keys(dataList[0])]}
    return(
        <table id={id} className="table-cust">
            <thead>
                <tr>
                {        
                    headers.map((header)=>(
                        <th key={header}>
                            {/* Use of Nullish Operator. If left-hand value is undefined, return right-hand value */}
                            {columnLabels[header]??titleCaseFormat(header)}
                        </th>
                    ))
                }
                </tr>
            </thead>
            <tbody>
                {dataList.map((entry,index)=>(
                    <tr key={entry.id}>
                        {/*Object.keys(entry) gives a list of entry object's keys. If the key is "is_admin"
                        Then return Admin or User, for any other key just return the value*/}
                        {
                            Object.keys(entry).map((key)=>(
                                <td key={key}>
                                    {/* Makes use of a object to map different keys to different functions.
                                        "is_admin" maps to Admin or User based on its value, while "id" returns index+1.
                                        If a value for the key doesn't exist, then default to returning entry[key]*/}
                                    {
                                        columnFormatter[key]?
                                        columnFormatter[key](entry[key],index):
                                        entry[key]
                                    }
                                </td>
                            ))
                        }
                        {props.deleteEntry?
                            (<td> 
                                {/* don't allow admins to delete admins*/}
                                {!entry.is_admin?
                                    (
                                    <button className="table-delete-button" onClick={()=>props.deleteEntry(entry.id)}>
                                    Delete
                                    </button>
                                    ):
                                    (<span>Protected</span>)
                                }
                            </td>):null
                        }
                        
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export default TableFactory;
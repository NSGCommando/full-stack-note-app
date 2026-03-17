import { titleCaseFormat } from "../utils/utilFuncs";
import "../styles/Components.css"
function TableFactory({dataList, deleteEntry}){
    if(!dataList || dataList.length===0){return (<p>No data found</p>);}
    const headers = [...Object.keys(dataList[0]),"Actions"]
    return(
        <table className="table-cust">
            <thead>
                <tr>
                {        
                    headers.map((header)=>(
                        <th key={header}>
                            {header==="is_admin"?"Role":titleCaseFormat(header)}
                        </th>
                    ))
                }
                </tr>
            </thead>
            <tbody>
                {dataList.map((entry,index)=>(
                    <tr key={entry.id}>
                        {/*Object.keys(entry) gives a list of entry object's keys. If the key is "is_admin
                        Then return Admin or User, for any other key just return the value*/}
                        {
                            Object.keys(entry).map((key)=>(
                                <td key={key}>
                                    {key==="is_admin"?
                                        (entry[key]===true?"Admin":"User"):
                                        (key==="id"?index:entry[key])
                                    }
                                </td>
                            ))
                        }
                        <td> 
                            {/* don't allow admins to delete admins*/}
                            {!entry.is_admin?
                                (
                                <button className="user-delete-button" onClick={()=>deleteEntry(entry.id)}>
                                Delete
                                </button>
                                ):
                                (<span>Protected</span>)
                            }
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export default TableFactory;
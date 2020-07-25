from cffi import FFI
ffi = FFI()
converter = FFI()
ffi.cdef("""
		typedef int InteropContext;
		
		typedef struct {
	        const unsigned char *content;
	       	unsigned int len;
	    } InteropString;

	    typedef struct {
	        InteropString result_json;
	       	InteropString error_json;
	    } InteropJsonResponse;

	    InteropContext tc_create_context();
	    InteropContext tc_destroy_context(InteropContext context);
	    InteropJsonResponse *tc_json_request(InteropContext, InteropString, InteropString);
	    void tc_destroy_json_response(InteropJsonResponse *response);
	    InteropJsonResponse tc_read_json_response(InteropJsonResponse *response);
	"""
	)
converter.cdef("""
		struct InteropString 
{ 
   const unsigned char *content;
   unsigned int len;
}; 
  
struct InteropString convert(char string[]);  
	""")

def create_InteropString(string):
	obj = ffi.new("InteropString *")
	string_in_c = ffi.from_buffer(string.encode("utf-8"))
	obj.content = ffi.new("char[]",string.encode())
	obj.len = len(string.encode())
	return obj

conv = converter.dlopen("./libconvert.so")
lib = ffi.dlopen("./libton_client.so")
a = conv.convert(ffi.new("char[]","string".encode()))
result = lib.tc_create_context()
print(result)
a = lib.tc_json_request(result,a,a)
using System;

namespace SeleniumFramework.Core.Exceptions
{
    /// <summary>
    /// Thrown when a page fails to load within the expected timeout
    /// </summary>
    public class PageNotLoadedException : Exception
    {
        public PageNotLoadedException(string message) : base(message) { }
        
        public PageNotLoadedException(string message, Exception innerException) 
            : base(message, innerException) { }
    }
}

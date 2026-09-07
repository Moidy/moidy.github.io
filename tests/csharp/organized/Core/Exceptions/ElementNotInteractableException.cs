using System;

namespace SeleniumFramework.Core.Exceptions
{
    /// <summary>
    /// Thrown when an element cannot be interacted with (hidden, disabled, etc.)
    /// </summary>
    public class ElementNotInteractableException : Exception
    {
        public ElementNotInteractableException(string message) : base(message) { }
        
        public ElementNotInteractableException(string message, Exception innerException) 
            : base(message, innerException) { }
    }
}
